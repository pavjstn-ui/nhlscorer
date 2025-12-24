# NHLScorer — Project State & Rebuild Handover (FINAL)

This file documents **exactly what was built, decided, and proven** in the NHLScorer project.
It exists so the current chats can be deleted and the project can be rebuilt cleanly **without re-discovery or re-arguing setup**.

This is **project-specific**, not a generic bootstrap.

---

## 1. Project intent (locked)

**Project name:** `nhlscorer`  
**Goal:** Build a fast, data-driven NHL betting engine.

**Phase order (intentional):**
1. Team markets (h2h → totals → spreads) ✅ CURRENT
2. Player goalscorer markets ⏸ SEPARATE CHAT / LATER PHASE

---

## 2. What was attempted and why it changed

### Original idea
- Build **anytime goalscorer EV model**
- Use **The Odds API** + MoneyPuck player stats

### What was proven (important facts)
- The Odds API **does support NHL** (`icehockey_nhl`)
- Endpoint `/v4/sports/{sport}/odds` works for:
  - `h2h`
  - `totals`
  - `spreads`
- Market `player_goal_scorer_anytime` on that endpoint returns:
  - `422 INVALID_MARKET`

➡️ This is an **API limitation**, not a coding error.

### Decision
We **pivoted** to team markets to:
- avoid switching providers mid-project
- produce a working EV pipeline quickly
- preserve momentum

Player goalscorer work is **explicitly deferred**.

---

## 3. Current technical scope (what IS in scope)

### Markets
- ✅ h2h (moneyline) — ACTIVE
- ⏭ totals — next
- ⏭ spreads — later
- ❌ player props — NOT in this phase

### Data sources
- **Odds:** The Odds API (team markets)
- **Stats:** MoneyPuck (team + player stats already available)

---

## 4. Canonical folder structure (for THIS project)

```
nhlscorer/
├── core/
│   └── data_pipeline/
│       ├── nhl_pipeline.py        # MoneyPuck → team/player stats
│       └── nhl_odds_fetcher.py    # Odds API (h2h/totals/spreads)
├── data/
│   ├── raw/                       # API JSONs, raw CSVs (gitignored)
│   └── processed/                # Clean CSV outputs
│       ├── player_goal_rates.csv
│       └── nhl_h2h_board.csv      # target output
├── notebooks/
│   └── 03_h2h_board.ipynb         # main working notebook
├── docs/
├── README.md
├── requirements.txt
└── .venv/
```

There is **no `services/` folder anymore**.
Any reference to `services/nhl_goal_scorers` is obsolete and must be removed.

---

## 5. What already works (verified)

### Odds API
- API key valid
- NHL sport key valid
- Markets returning 200:
  - `h2h`
  - `totals`
  - `spreads`

### Pipeline logic
- Odds fetched → raw JSON
- Parsed to flat CSV
- h2h odds produce:
  - bookmaker
  - event_id
  - team name
  - decimal odds

### Known fact
h2h odds contain **teams + draw**, NOT player names.
This is correct and expected.

---

## 6. What failed (and should NOT be retried)

- Trying to join h2h odds with player stats ❌
- Expecting player names in h2h markets ❌
- Using `player_goal_scorer_anytime` on `/sports/{sport}/odds` ❌

These are resolved decisions, not open questions.

---

## 7. Immediate next objective (THIS CHAT SHOULD CONTINUE FROM HERE)

### Build **NHL H2H Board**

Single CSV output:

```
data/processed/nhl_h2h_board.csv
```

Each row = one game, containing:
- commence_time
- home_team
- away_team
- best_home_price + bookmaker
- best_away_price + bookmaker
- draw (if present)
- no-vig implied probabilities

This board is the **foundation** for EV.

---

## 8. How EV will be added (later, simple first)

- Add team-strength signal:
  - MoneyPuck xG
  - goal differential
  - home/away adjustment
- Compare model probability vs best odds
- Rank by EV

No ML yet. No over-engineering.

---

## 9. Player goalscorer work (explicitly deferred)

Player goalscorer odds require:
- The Odds API `/events/{eventId}/odds` flow, OR
- A different provider (Sportradar, SportsDataIO, OddsJam)

This will be done in a **new chat**, using a separate handover file.

---

## 10. How to restart cleanly with a new assistant

Paste this file and say:

> “This is the full state of the nhlscorer project.  
> Continue from section 7. Do not revisit setup or pivot decisions.”

---

## Final note (human, not technical)

Time was lost on:
- unclear scope boundaries
- repeated setup
- mixing architecture with execution

This file exists so that **does not happen again** for this project.

Everything above is **locked context**.
