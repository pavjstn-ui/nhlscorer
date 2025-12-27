import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def scrape_powerplay_units(team_slug: str) -> dict:
    """
    Scrape DailyFaceoff line-combinations page for one team and return PP1/PP2 lists.
    """
    url = f"https://www.dailyfaceoff.com/teams/{team_slug}/line-combinations/"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    def grab_five_after_heading(heading_text: str) -> list[str]:
        heading = soup.find(string=lambda s: isinstance(s, str) and s.strip() == heading_text)
        if not heading:
            return []
        players = []
        for el in heading.parent.find_all_next("a"):
            name = el.get_text(strip=True)
            if name:
                players.append(name)
            if len(players) == 5:
                break
        return players

    return {
        "team_slug": team_slug,
        "pp1": grab_five_after_heading("1st Powerplay Unit"),
        "pp2": grab_five_after_heading("2nd Powerplay Unit"),
    }

def rows_from_pp(team_abbrev: str, pp1: list[str], pp2: list[str]) -> list[dict]:
    rows = []
    for name in pp1:
        rows.append({"player": name, "team": team_abbrev, "pp_unit": 1})
    for name in pp2:
        rows.append({"player": name, "team": team_abbrev, "pp_unit": 2})
    return rows

def scrape_all_teams_pp(target_date: str, slug_to_abbrev: dict[str, str], sleep_s: float = 0.8) -> pd.DataFrame:
    all_rows = []
    errors = []

    for slug, abbrev in slug_to_abbrev.items():
        try:
            res = scrape_powerplay_units(slug)
            pp1, pp2 = res["pp1"], res["pp2"]

            # Basic validation: expect 5 + 5
            if len(pp1) != 5 or len(pp2) != 5:
                errors.append({"team": abbrev, "slug": slug, "pp1_len": len(pp1), "pp2_len": len(pp2)})
            all_rows.extend(rows_from_pp(abbrev, pp1, pp2))

            time.sleep(sleep_s)
        except Exception as e:
            errors.append({"team": abbrev, "slug": slug, "error": str(e)})

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["player", "team", "pp_unit"])
    # Optional: store errors to inspect later
    if errors:
        err_df = pd.DataFrame(errors)
        err_df.to_csv(f"inputs/dailyfaceoff_pp_errors_{target_date}.csv", index=False)

    out_path = f"inputs/dailyfaceoff_pp_{target_date}.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

    if errors:
        print(f"Warnings: {len(errors)} teams had issues. See inputs/dailyfaceoff_pp_errors_{target_date}.csv")

    return df

# --- Slug → team abbreviation mapping (start list) ---
# Add/adjust if any slug differs; errors file will tell you.
slug_to_abbrev = {
    "anaheim-ducks": "ANA",
    "arizona-coyotes": "ARI",  # note: may be legacy, adjust if DailyFaceoff changed
    "boston-bruins": "BOS",
    "buffalo-sabres": "BUF",
    "calgary-flames": "CGY",
    "carolina-hurricanes": "CAR",
    "chicago-blackhawks": "CHI",
    "colorado-avalanche": "COL",
    "columbus-blue-jackets": "CBJ",
    "dallas-stars": "DAL",
    "detroit-red-wings": "DET",
    "edmonton-oilers": "EDM",
    "florida-panthers": "FLA",
    "los-angeles-kings": "LAK",
    "minnesota-wild": "MIN",
    "montreal-canadiens": "MTL",
    "nashville-predators": "NSH",
    "new-jersey-devils": "NJD",
    "new-york-islanders": "NYI",
    "new-york-rangers": "NYR",
    "ottawa-senators": "OTT",
    "philadelphia-flyers": "PHI",
    "pittsburgh-penguins": "PIT",
    "san-jose-sharks": "SJS",
    "seattle-kraken": "SEA",
    "st-louis-blues": "STL",
    "tampa-bay-lightning": "TBL",
    "toronto-maple-leafs": "TOR",
    "vancouver-canucks": "VAN",
    "vegas-golden-knights": "VGK",
    "washington-capitals": "WSH",
    "winnipeg-jets": "WPG",
}

# Run it
df_all = scrape_all_teams_pp("2025-12-28", slug_to_abbrev)
print(df_all.head(10))
