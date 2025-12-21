# NHL Goal Scorer

# nhlscorer

Fast, data-driven NHL betting engine.

This repository currently focuses on **team-level markets** (moneyline / h2h),
with a clear path to EV calculation and later expansion to totals, spreads,
and player goalscorer markets.

---

## 🎯 Current Scope (LOCKED)

### Active
- ✅ NHL **h2h (moneyline)** markets
- Odds sourced from **The Odds API**
- Best-price aggregation across bookmakers
- No-vig (fair) implied probabilities

### Deferred (separate phase / separate chat)
- ❌ Player goalscorer props
- ❌ Anytime goalscorer EV
- ❌ Player-level odds joins

These are intentionally postponed due to API limitations on the standard odds endpoint.

---

## 📁 Repository Structure

nhlscorer/
├── core/
│ └── data_pipeline/
│ ├── nhl_odds_fetcher.py # Fetches NHL odds (h2h / totals / spreads)
│ └── nhl_pipeline.py # Stats pipelines (MoneyPuck)
├── data/
│ ├── raw/ # Raw API JSONs, raw CSVs (gitignored)
│ └── processed/ # Clean outputs
│ ├── player_goal_rates.csv
│ └── nhl_h2h_board.csv # MAIN OUTPUT (to be built)
├── notebooks/
│ └── 03_h2h_board.ipynb # h2h board construction & inspection
├── docs/
├── requirements.txt
└── .venv/


There is **no `services/` folder**.  
Any reference to `services/nhl_goal_scorers` is obsolete.

---

## 🧠 Data Sources

- **Odds:** The Odds API  
  - Supported markets: `h2h`, `totals`, `spreads`
- **Stats:** MoneyPuck (team & player stats)

---

## 🧪 Environment & Jupyter

- Python environment: local `.venv`
- Jupyter kernel: `Python (nhlscorer)`
- Jupyter is always started from repo root:
  ```bash
  cd ~/Projects/nhlscorer
  source .venv/bin/activate
  jupyter lab
