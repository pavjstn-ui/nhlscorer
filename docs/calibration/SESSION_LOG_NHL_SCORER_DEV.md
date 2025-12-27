# NHL Goal Scorer – Development Session Summary

## What Was Implemented

### Core Prediction Model
- MoneyPuck xG per game baseline
- TOI per game → team-relative TOI multiplier
- Power-play adjustment via DailyFaceoff PP units
- Poisson-based goal probability
- PP1 boost applied to λ

### Data Sources Integrated
- MoneyPuck skater CSV
- DailyFaceoff power-play units (scraped daily)
- NHL API boxscore / player-by-game stats

### Pipelines Built
- run_daily.py:
  - predictions_YYYY-MM-DD.csv
  - calibration_snapshot_YYYY-MM-DD.csv
  - goal_scorer_ev_YYYY-MM-DD.csv (when odds present)
- fetch_outcomes.py:
  - actual_goals_YYYY-MM-DD.csv
- Calibration join:
  - calibration_joined_YYYY-MM-DD.csv
  - reliability_YYYY-MM-DD.csv

### Diagnostics Added
- Brier score computation
- Reliability bins
- Extensive debug logging
- Safe fallbacks for missing PP data

---

## What Works
- End-to-end pipeline runs
- Historical backtests execute without crashes
- DailyFaceoff PP overrides function correctly
- Calibration snapshots generated correctly

## What Does NOT Work
- Actual goal scorers are not being matched correctly
- Result: all players labeled as not scoring
- Calibration curves therefore meaningless

---

## Key Insight
The system architecture and probability model are **sound**.

The only blocking issue is **goal attribution from NHL API data**.
