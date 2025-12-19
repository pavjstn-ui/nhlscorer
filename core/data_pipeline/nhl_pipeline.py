from __future__ import annotations

from pathlib import Path
import pandas as pd


def run_moneypuck_goal_rates_pipeline(
    season_label: str = "2023_2024",
    input_filename: str = "moneypuck_skaters_2023_2024_regular.csv",
    output_filename: str = "player_goal_rates.csv",
) -> Path:
    """
    Load MoneyPuck season skaters CSV, filter to situation == 'all',
    compute simple per-game goal scoring rates, and save to processed CSV.

    Returns the output path.
    """

    # 1) Define the project root reliably based on THIS file location.
    #    This avoids needing to run the script from a specific working directory.
    project_root = Path(__file__).resolve().parents[2]

    # 2) Define input/output directories using the repo conventions.
    raw_dir = project_root / "services" / "nhl_goal_scorers" / "data" / "raw"
    processed_dir = project_root / "services" / "nhl_goal_scorers" / "data" / "processed"

    # 3) Ensure the processed folder exists so saving never fails.
    processed_dir.mkdir(parents=True, exist_ok=True)

    # 4) Build the full input/output paths.
    input_path = raw_dir / input_filename
    output_path = processed_dir / output_filename

    # 5) Fail fast with a helpful message if the CSV isn't there.
    if not input_path.exists():
        raise FileNotFoundError(
            f"MoneyPuck CSV not found at: {input_path}\n"
            f"Expected raw data in: {raw_dir}\n"
            f"Tip: download the file and place it there (raw files are NOT committed)."
        )

    # 6) Load the data.
    df = pd.read_csv(input_path)

    # 7) Verify required columns exist (prevents silent wrong results).
    required_cols = [
        "playerId",
        "name",
        "team",
        "position",
        "situation",
        "games_played",
        "I_F_goals",
        "I_F_shotsOnGoal",
        "I_F_xGoals",
        "icetime",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            "MoneyPuck CSV is missing required columns:\n"
            f"{missing}\n"
            "This usually means the CSV format changed or a different file was downloaded."
        )

    # 8) Keep only one row per player: situation == 'all'
    df_all = df[df["situation"] == "all"].copy()

    # 9) Keep only the minimal set of columns we care about for v1.
    base_cols = [
        "playerId",
        "name",
        "team",
        "position",
        "games_played",
        "I_F_goals",
        "I_F_shotsOnGoal",
        "I_F_xGoals",
        "icetime",
    ]
    df_base = df_all[base_cols].copy()

    # 10) Compute the same metrics as the notebook.
    #     We guard against division-by-zero for shooting %.
    df_base["goals_per_game"] = df_base["I_F_goals"] / df_base["games_played"]
    df_base["shots_per_game"] = df_base["I_F_shotsOnGoal"] / df_base["games_played"]

    # shooting_pct = goals / shots_on_goal
    # If shots == 0, set shooting_pct to 0 to avoid inf/NaN.
    shots = df_base["I_F_shotsOnGoal"]
    df_base["shooting_pct"] = (df_base["I_F_goals"] / shots).where(shots > 0, 0.0)

    # 11) Save to processed CSV.
    df_base.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":
    out = run_moneypuck_goal_rates_pipeline()
    print(f"Saved: {out}")
