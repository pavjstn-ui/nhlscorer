#!/usr/bin/env python3
"""
run_daily.py
------------
Strict daily runner for NHL goal scorer model.

Behavior (as requested):
- Requires --date YYYY-MM-DD
- Runs predictions-only every time
- If odds file is missing: FAIL LOUDLY (exit with message)
- Writes outputs to data/processed/ (gitignored)
- Appends logs to logs/predictions_log.csv (LOCAL ONLY; gitignored)
"""

from __future__ import annotations
from datetime import timezone  # put this at the top imports
import argparse
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import requests


# -----------------------------
# Helpers
# -----------------------------

def ensure_dir(path: Path) -> None:
    """Create a directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)


def iso_today_utc() -> str:
    """Return today's date in UTC as YYYY-MM-DD."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def normalize_name(s: str) -> str:
    """Basic name normalization for joins."""
    if pd.isna(s):
        return ""
    return str(s).strip().lower()

def load_dailyfaceoff_pp(paths: Paths, target_date: str) -> pd.DataFrame:
    """
    Load DailyFaceoff powerplay units for a given date.

    Expected file:
      inputs/dailyfaceoff_pp_YYYY-MM-DD.csv
    Columns:
      player, team, pp_unit (1 or 2)
    """
    pp_path = paths.inputs / f"dailyfaceoff_pp_{target_date}.csv"
    if not pp_path.exists():
        raise FileNotFoundError(f"Missing DailyFaceoff PP file: {pp_path}")

    df = pd.read_csv(pp_path)
    df["player_norm"] = df["player"].map(normalize_name)
    df["team"] = df["team"].astype(str).str.upper()
    df["pp_unit"] = pd.to_numeric(df["pp_unit"], errors="coerce").fillna(0).astype(int)

    return df[["player", "player_norm", "team", "pp_unit"]]
  


@dataclass(frozen=True)
class Paths:
    project_root: Path
    data_raw: Path
    data_processed: Path
    inputs: Path
    logs: Path


def get_paths() -> Paths:
    """
    Resolve project paths relative to this script file:
    core/data_pipeline/run_daily.py -> project root is 2 parents up.
    """
    script_path = Path(__file__).resolve()
    project_root = script_path.parents[2]
    return Paths(
        project_root=project_root,
        data_raw=project_root / "data" / "raw",
        data_processed=project_root / "data" / "processed",
        inputs=project_root / "inputs",
        logs=project_root / "logs",
    )


# -----------------------------
# NHL + MoneyPuck loading
# -----------------------------

def load_moneypuck_skaters_csv(paths: Paths) -> pd.DataFrame:
    """
    Load MoneyPuck skaters CSV from data/raw/skaters.csv.
    """
    skaters_path = paths.data_raw / "skaters.csv"
    if not skaters_path.exists():
        raise FileNotFoundError(
            f"Missing MoneyPuck file: {skaters_path}\n"
            "Put skaters.csv into data/raw/ (kept local, not committed)."
        )
    mp = pd.read_csv(skaters_path)
    return mp


def fetch_nhl_schedule_now() -> dict:
    """
    Fetch current NHL schedule block (official API).
    Note: This returns 'now' schedule window, not arbitrary date.
    """
    url = "https://api-web.nhle.com/v1/schedule/now"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_teams_for_date(schedule_json: dict, target_date: str) -> set[str]:
    """
    Extract team abbreviations for games on target_date (YYYY-MM-DD)
    from schedule['gameWeek'].
    """
    teams = set()
    for day in schedule_json.get("gameWeek", []):
        # day might contain date like "2025-12-24"
        day_date = day.get("date")
        if day_date != target_date:
            continue
        for game in day.get("games", []):
            away = game.get("awayTeam", {}).get("abbrev")
            home = game.get("homeTeam", {}).get("abbrev")
            if away:
                teams.add(away)
            if home:
                teams.add(home)
    return teams


# -----------------------------
# Model: predictions-only (same logic as your status doc)
# -----------------------------

def build_predictions(mp: pd.DataFrame, teams_today: set[str], pp_df: pd.DataFrame | None = None) -> pd.DataFrame:

    """
    Build player goal probabilities using MoneyPuck xG per game + PP1 boost.

    This is intentionally simple and deterministic (no ML).
    """
    # Filter to "all" situation for base player rows
    mp_all = mp[mp["situation"] == "all"].copy()

    # Keep only players whose teams play today
    todays_players = mp_all[mp_all["team"].isin(teams_today)].copy()

    # Guard against division by zero
    todays_players["games_played"] = todays_players["games_played"].replace(0, pd.NA)

    # Base xG per game
    todays_players["xg_per_game"] = (
        todays_players["I_F_xGoals"] / todays_players["games_played"]
    ).fillna(0.0)

    # ---- TOI opportunity features (from MoneyPuck icetime) ----
    todays_players["toi_per_game"] = (
        todays_players["icetime"] / todays_players["games_played"]
    ).fillna(0.0)

    todays_players["team_avg_toi_per_game"] = todays_players.groupby("team")["toi_per_game"].transform("mean")

    todays_players["toi_ratio"] = (
        todays_players["toi_per_game"] / todays_players["team_avg_toi_per_game"]
    ).replace([pd.NA, float("inf")], 0.0).fillna(0.0)

    todays_players["toi_multiplier"] = todays_players["toi_ratio"].clip(lower=0.6, upper=1.4)


    # Determine PP1 via 5on4 icetime rank (top 5 per team)
    mp_pp = mp[mp["situation"] == "5on4"].copy()
    mp_pp["pp_toi_rank"] = mp_pp.groupby("team")["icetime"].rank(
        ascending=False, method="min"
    )
    mp_pp["is_pp1"] = (mp_pp["pp_toi_rank"] <= 5).astype(int)

    # Merge PP1 indicator (by name)
    todays_players = todays_players.merge(
        mp_pp[["name", "is_pp1"]],
        on="name",
        how="left",
    )
    todays_players["is_pp1"] = todays_players["is_pp1"].fillna(0).astype(int)

    # --- Override PP unit from DailyFaceoff if provided ---
    if pp_df is not None and not pp_df.empty:
        # Merge by normalized name + team
        todays_players["player_norm"] = todays_players["name"].map(normalize_name)
        todays_players = todays_players.merge(
            pp_df[["player_norm", "team", "pp_unit"]],
            left_on=["player_norm", "team"],
            right_on=["player_norm", "team"],
            how="left",
        )

    # DailyFaceoff wins when available
    todays_players["is_pp1"] = (todays_players["pp_unit"] == 1).astype(int)

    # Optional: keep PP2 flag for later modeling
    todays_players["is_pp2"] = (todays_players["pp_unit"] == 2).astype(int)

    # If pp_unit missing (NaN), fallback to MoneyPuck inference
    # (so we don’t accidentally set everyone to 0)
    missing_pp = todays_players["pp_unit"].isna()
    todays_players.loc[missing_pp, "is_pp1"] = todays_players.loc[missing_pp, "is_pp1"].fillna(0).astype(int)
    todays_players.loc[missing_pp, "is_pp2"] = 0
else:
    todays_players["is_pp2"] = 0


    # Apply PP1 boost (50% increase), cap at 0.35
    # Note: We'll improve calibration later using Poisson transform.
    # Apply PP1 boost on the rate (lambda), then Poisson -> probability
    pp1_boost = 0.5
    todays_players["lambda_goal"] = (
    todays_players["xg_per_game"]
    * todays_players["toi_multiplier"]
    * (1 + todays_players["is_pp1"] * pp1_boost)
    )

    todays_players["goal_probability"] = (1 - np.exp(-todays_players["lambda_goal"])).clip(upper=0.35)



    # Normalized name for downstream merges
    todays_players["name_norm"] = todays_players["name"].map(normalize_name)
    # Debug: confirm columns exist
    assert "lambda_goal" in todays_players.columns, "lambda_goal was not created"
    assert "goal_probability" in todays_players.columns, "goal_probability was not created"

    return todays_players

def append_predictions_log(paths: Paths, target_date: str, pred: pd.DataFrame) -> None:
    ensure_dir(paths.logs)
    log_path = paths.logs / "predictions_log.csv"

    out = pred.copy()
    out.insert(0, "date", target_date)
    out.insert(1, "logged_at_utc", datetime.now(timezone.utc).isoformat(timespec="seconds"))


    keep = [
        "date",
        "logged_at_utc",
        "name",
        "team",
        "xg_per_game",
        "toi_per_game",
        "toi_multiplier",
        "lambda_goal",
        "goal_probability",
        "is_pp1",
    ]

    out = out[keep].rename(columns={"name": "player"})

    write_header = not log_path.exists()
    out.to_csv(log_path, mode="a", index=False, header=write_header)

# -----------------------------
# Odds + EV
# -----------------------------

def load_manual_odds(paths: Paths, target_date: str) -> pd.DataFrame:
    """
    Load manual odds CSV.
    Strict mode: file must exist, otherwise we fail loudly.
    Naming convention: inputs/manual_odds_YYYY-MM-DD.csv
    """
    odds_path = paths.inputs / f"manual_odds_{target_date}.csv"
    if not odds_path.exists():
        raise FileNotFoundError(
            f"Missing odds file: {odds_path}\n"
            "Create it from OCR with columns: player,odds\n"
            "Example: inputs/manual_odds_YYYY-MM-DD.csv"
        )

    odds_df = pd.read_csv(odds_path)

    required = {"player", "odds"}
    missing = required - set(odds_df.columns)
    if missing:
        raise ValueError(
            f"Odds file missing required columns {missing}. Found: {list(odds_df.columns)}"
        )

    odds_df = odds_df.copy()
    odds_df["player_norm"] = odds_df["player"].map(normalize_name)
    odds_df["odds"] = pd.to_numeric(odds_df["odds"], errors="coerce")
    odds_df = odds_df.dropna(subset=["odds", "player_norm"])

    # Basic sanity bounds
    odds_df = odds_df[(odds_df["odds"] >= 1.01) & (odds_df["odds"] <= 50)]

    return odds_df


def merge_and_calculate_ev(pred: pd.DataFrame, odds_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge predictions with odds and compute EV.
    """
    merged = odds_df.merge(
        pred[
            [
                "name_norm",
                "name",
                "team",
                "goal_probability",
                "lambda_goal",
                "I_F_goals",
                "games_played",
                "is_pp1",
            ]
        ],
        left_on="player_norm",
        right_on="name_norm",
        how="inner",
    )

    merged["implied_prob"] = 1 / merged["odds"]
    merged["ev"] = (merged["goal_probability"] * merged["odds"]) - 1
    merged["ev_percent"] = merged["ev"] * 100

    return merged


# -----------------------------
# Logging
# -----------------------------

def append_log(paths: Paths, target_date: str, merged: pd.DataFrame) -> None:
    """
    Append merged rows to logs/predictions_log.csv (local only).
    """
    ensure_dir(paths.logs)
    log_path = paths.logs / "predictions_log.csv"

    log_df = merged.copy()
    log_df.insert(0, "date", target_date)
    log_df.insert(1, "logged_at_utc", datetime.utcnow().isoformat(timespec="seconds"))

    # Keep log schema stable and compact
    keep_cols = [
        "date",
        "logged_at_utc",
        "player",
        "team",
        "odds",
        "implied_prob",
        "goal_probability",
        "lambda_goal",
        "ev",
        "ev_percent",
        "is_pp1",
    ]
    for col in keep_cols:
        if col not in log_df.columns:
            log_df[col] = pd.NA
    log_df = log_df[keep_cols]

    write_header = not log_path.exists()
    log_df.to_csv(log_path, mode="a", index=False, header=write_header)


# -----------------------------
# Main
# -----------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NHL goal scorer daily runner")
    parser.add_argument(
        "--date",
        required=True,
        help="Target date in YYYY-MM-DD (must exist in NHL schedule/now window).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=25,
        help="How many top predictions to print to console (default 25).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target_date = args.date.strip()

    # Basic date validation
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        print("ERROR: --date must be in YYYY-MM-DD format.", file=sys.stderr)
        return 2

    paths = get_paths()

    # Ensure output dirs exist (gitignored)
    ensure_dir(paths.data_processed)
    ensure_dir(paths.inputs)
    ensure_dir(paths.logs)

    # Load MoneyPuck
    mp = load_moneypuck_skaters_csv(paths)

    # Fetch schedule and extract teams for target_date
    schedule = fetch_nhl_schedule_now()
    teams_today = extract_teams_for_date(schedule, target_date)

    if not teams_today:
        print(
            f"ERROR: No games found for {target_date} in schedule/now window.\n"
            "Try again closer to game day, or adjust schedule endpoint strategy.",
            file=sys.stderr,
        )
        return 3

    # Load DailyFaceoff PP units (fail loudly if missing)
    pp_df = load_dailyfaceoff_pp(paths, target_date)

    # Predictions-only (DailyFaceoff PP overrides MoneyPuck where available)
    pred = build_predictions(mp, teams_today, pp_df=pp_df)

    pred_out = paths.data_processed / f"predictions_{target_date}.csv"
    pred.sort_values("goal_probability", ascending=False).to_csv(pred_out, index=False)


    # ✅ NEW: log predictions BEFORE odds (so it still logs even if odds are missing)
    append_predictions_log(paths, target_date, pred)
    print(f"Appended predictions log: {paths.logs / 'predictions_log.csv'}")

    # Console preview
    print("\n🎯 TOP PREDICTIONS (probability ranking)")
    preview = pred.sort_values("goal_probability", ascending=False)[
        ["name","team","xg_per_game","toi_per_game","toi_multiplier","lambda_goal","goal_probability","is_pp1"]
    ].head(args.top)
    print(preview.to_string(index=False))

    print(f"\nSaved predictions: {pred_out}")

    # Strict odds load (fail loudly if missing)
    odds_df = load_manual_odds(paths, target_date)


    # Strict odds load (fail loudly if missing)
    odds_df = load_manual_odds(paths, target_date)

    merged = merge_and_calculate_ev(pred, odds_df)

    merged_out = paths.data_processed / f"goal_scorer_ev_{target_date}.csv"
    merged.sort_values("ev_percent", ascending=False).to_csv(merged_out, index=False)

    positive_ev = merged[merged["ev"] > 0].sort_values("ev_percent", ascending=False)
    pos_out = paths.data_processed / f"positive_ev_{target_date}.csv"
    positive_ev.to_csv(pos_out, index=False)

    print("\n✅ EV RESULTS")
    print(f"Matched odds rows: {len(merged)}")
    print(f"Positive EV rows:  {len(positive_ev)}")
    if len(positive_ev) > 0:
        print("\nTop 20 positive EV:")
        print(
            positive_ev[
                ["player", "team", "odds", "implied_prob", "lambda_goal", "goal_probability", "ev_percent", "is_pp1"]
            ]
            .head(20)
            .to_string(index=False)
        )

    print(f"\nSaved EV table:     {merged_out}")
    print(f"Saved positive EV:  {pos_out}")

    # Log (local only)
    append_log(paths, target_date, merged)

    print(f"\nAppended log: {paths.logs / 'predictions_log.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())