from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
from unidecode import unidecode
import re

def normalize_name(name: str) -> str:
    if not isinstance(name, str):
        return ""

    s = unidecode(name)          # remove accents
    s = s.lower()

    # remove anything in brackets like (NYR) or [NYR]
    s = re.sub(r"[\(\[].*?[\)\]]", "", s)

    # keep letters/spaces only
    s = re.sub(r"[^a-z\s]", " ", s)

    # collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()

    return s



def main() -> None:
    root = project_root()

    stats_path = root / "data" / "processed" / "player_signal_table.csv"
    odds_path = root / "data" / "processed" / "odds_anytime_goalscorer.csv"
    out_path = root / "data" / "processed" / "anytime_goalscorer_ev.csv"

    if not stats_path.exists():
        raise FileNotFoundError(stats_path)
    if not odds_path.exists():
        raise FileNotFoundError(odds_path)

    stats = pd.read_csv(stats_path)
    odds = pd.read_csv(odds_path)

    # Normalize names for join
    stats["player_key"] = stats["name"].map(normalize_name)
    odds["player_key"] = odds["player_name"].map(normalize_name)

    # Implied probability from decimal odds
    odds["implied_prob"] = 1.0 / odds["price_decimal"]

    # Join
    merged = odds.merge(
        stats,
        on="player_key",
        how="inner",
        suffixes=("_odds", "_stats"),
    )

    # Simple probability proxy from signal (bounded)
    merged["model_prob"] = merged["signal"].clip(0.01, 0.95)

    # Expected Value (decimal odds)
    merged["ev"] = (
        merged["model_prob"] * merged["price_decimal"] - 1.0
    )

    cols = [
        "player_name",
        "team",
        "price_decimal",
        "implied_prob",
        "model_prob",
        "ev",
        "bookmaker",
        "commence_time",
    ]

    merged = merged[cols].sort_values("ev", ascending=False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(out_path, index=False)

    print("Rows:", len(merged))
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
