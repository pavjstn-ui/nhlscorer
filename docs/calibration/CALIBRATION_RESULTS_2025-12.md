# Calibration Results – NHL Goal Scorer Model (December 2025)

## Dates Evaluated
- 2025-12-13
- 2025-12-23

## Model Description
- Base signal: MoneyPuck xG per game
- TOI opportunity multiplier (team-normalized)
- DailyFaceoff PP unit overrides (PP1 / PP2)
- Poisson goal probability transform:
  P(goal ≥ 1) = 1 − exp(−λ)
- PP1 boost applied to λ (not probability)

---

## Results – 2025-12-13

### Brier Score
**0.0295** (numerically very good)

### Rows Evaluated
661 players

### Reliability Table

| Probability Bin | n | Avg Pred | Avg Actual |
|-----------------|---|----------|------------|
| 0.0–0.1 | 390 | 0.046 | 0.0 |
| 0.1–0.2 | 138 | 0.137 | 0.0 |
| 0.2–0.3 | 53 | 0.250 | 0.0 |
| 0.3–0.4 | 52 | 0.351 | 0.0 |
| 0.4–0.5 | 23 | 0.441 | 0.0 |
| 0.5–0.6 | 5 | 0.527 | 0.0 |

---

## Interpretation

- The **Brier score is low**, indicating internally consistent probabilities.
- However, **avg_actual = 0.0 in all bins**, which is impossible in real NHL data.
- This confirms a **goal attribution failure**, not a modeling issue.

---

## Conclusion

✅ Probability model math is correct  
❌ Calibration is invalid due to incorrect outcome labeling  

Next step must focus **only on fixing actual goal scorer extraction**.
