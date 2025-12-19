from __future__ import annotations

import json
from pathlib import Path
import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def parse_anytime_goalscorer_odds_json(json_path: Path) -> pd.DataFrame:
    """
    Parse The Odds API odds response for player anytime goalscorer.

    Output columns (best-effort, based on available fields):
    - event_id, commence_time, home_team, away_team
    - bookmaker, market_key
    - player_name, price_decimal

    Notes:
    - The Odds API payload format can vary by market.
    - This parser is defensive: it skips missing pieces rather than crashing.
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))

    rows = []

    for event in data:
        event_id = event.get("id")
        commence_time = event.get("commence_time")
        home_team = event.get("home_team")
        away_team = event.get("away_team")

        bookmakers = event.get("bookmakers", []) or []
        for bm in bookmakers:
            bookmaker = bm.get("key") or bm.get("title") or "unknown"

            markets = bm.get("markets", []) or []
            for m in markets:
                market_key = m.get("key")

                outcomes = m.get("outcomes", []) or []
                for o in outcomes:
                    # For player props, outcome name is usually the player name
                    player_name = o.get("name")
                    price = o.get("price")  # decimal odds

                    if player_name is None or price is None:
                        continue

                    rows.append(
                        {
                            "event_id": event_id,
                            "commence_time": commence_time,
                            "home_team": home_team,
                            "away_team": away_team,
                            "bookmaker": bookmaker,
                            "market_key": market_key,
                            "player_name": player_name,
                            "price_decimal": price,
                        }
                    )

    return pd.DataFrame(rows)


def main() -> None:
    root = project_root()

    raw_path = root / "data" / "raw" / "odds_anytime_goalscorer_2025_12_19.json"
    out_path = root / "data" / "processed" / "odds_anytime_goalscorer.csv"

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw odds JSON not found: {raw_path}")

    df = parse_anytime_goalscorer_odds_json(raw_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)

    print("Parsed rows:", len(df))
    print("Saved:", out_path)


if __name__ == "__main__":
    main()
