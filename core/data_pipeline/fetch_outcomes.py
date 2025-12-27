import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests


def normalize_name(name: str) -> str:
    """
    Normalize player names so you can merge outcomes with predictions reliably.
    This is a simple version; you can expand it later (accents, suffixes, etc.).
    """
    if not isinstance(name, str):
        return ""
    return (
        name.strip()
        .lower()
        .replace(".", "")
        .replace("-", " ")
        .replace("’", "'")
    )


def nhl_get_json(url: str, timeout: int = 30) -> dict:
    """Small wrapper around requests.get() with a user-agent and basic error handling."""
    headers = {"User-Agent": "nhlscorer/1.0 (outcomes collector)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def get_game_ids_for_date(target_date: str) -> list[int]:
    """
    Fetch NHL game IDs for a given date (YYYY-MM-DD) from NHL schedule endpoint.
    """
    url = f"https://api-web.nhle.com/v1/schedule/{target_date}"
    data = nhl_get_json(url)

    # The schedule response groups games into "gameWeek" days.
    game_ids: list[int] = []
    for day in data.get("gameWeek", []):
        if day.get("date") != target_date:
            continue
        for g in day.get("games", []):
            gid = g.get("id")
            if isinstance(gid, int):
                game_ids.append(gid)

    return game_ids


def parse_boxscore_player_goals(box: dict, target_date: str, game_id: int) -> list[dict]:
    rows: list[dict] = []

    pbg = box.get("playerByGameStats", {})

    for side in ["awayTeam", "homeTeam"]:
        tb = pbg.get(side, {})
        team_abbr = tb.get("teamAbbrev", {}).get("default", "")  # sometimes missing; fallback below

        # If team abbrev isn't here, pull it from the top-level team block
        if not team_abbr:
            top_team = box.get(side, {})
            team_abbr = top_team.get("abbrev", "") or top_team.get("teamAbbrev", {}).get("default", "")

        # Skaters live in forwards + defense
        skaters = []
        skaters.extend(tb.get("forwards", []))
        skaters.extend(tb.get("defense", []))

        for p in skaters:
            name = p.get("fullName") or p.get("name", {}).get("default") or ""
            goals = p.get("goals", 0)

            player_id = p.get("playerId")

            rows.append({
                "date": target_date,
                "game_id": game_id,
                "team": str(team_abbr).upper(),
                "player_id": player_id,          # <-- add this
                "player": name,
                "player_norm": normalize_name(name),
                "goals": int(goals) if goals is not None else 0,
            })


    return rows



def fetch_outcomes_for_date(target_date: str) -> pd.DataFrame:
    """
    Main collector:
    - gets game IDs
    - downloads each boxscore
    - extracts goals for every player
    """
    game_ids = get_game_ids_for_date(target_date)

    all_rows: list[dict] = []
    for gid in game_ids:
        box_url = f"https://api-web.nhle.com/v1/gamecenter/{gid}/boxscore"
        box = nhl_get_json(box_url)
        all_rows.extend(parse_boxscore_player_goals(box, target_date, gid))

    if not all_rows:
        return pd.DataFrame(columns=["date", "game_id", "team", "player", "player_norm", "goals"])

    df = pd.DataFrame(all_rows)

    # Combine duplicates safely (sometimes payload can include repeated entries)
    df = (
        df.groupby(
            ["date", "game_id", "team", "player_id", "player", "player_norm"],
            as_index=False
        )["goals"]
        .sum()
        .sort_values(["date", "team", "player"])
    )

    # Add metadata
    df.insert(1, "collected_at_utc", datetime.now(timezone.utc).isoformat(timespec="seconds"))

    return df


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch actual goals per player from NHL API.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD (game date)")
    args = parser.parse_args()

    target_date = args.date.strip()

    df = fetch_outcomes_for_date(target_date)

    out_dir = Path("data") / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / f"actual_goals_{target_date}.csv"
    df.to_csv(out_path, index=False)

    print(f"Saved outcomes: {out_path}  (rows={len(df)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
