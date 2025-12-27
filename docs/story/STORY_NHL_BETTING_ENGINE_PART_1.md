# NHL Betting Engine – Evolution (Part 1)
**From Heuristics to Calibrated Probabilities**

---

## Background

This project began with a simple goal:

> Build a deterministic, explainable NHL anytime goal scorer model  
> that does NOT rely on machine learning.

The constraints were intentional:
- Full transparency
- No black-box ML
- Easy calibration and validation
- Manual bet placement (human-in-the-loop)

---

## Phase 1 – Baseline Model

The initial model used:
- MoneyPuck skater expected goals (xG)
- Games played normalization
- Simple PP1 inference via 5v4 ice time
- Linear scaling of xG → probability

This worked mechanically, but had **two critical flaws**:
1. Probabilities were not well calibrated
2. Power-play inference was noisy and unstable

---

## Phase 2 – Structural Improvements

### Poisson Goal Modeling
The model switched from linear probability scaling to:

P(goal ≥ 1) = 1 − exp(−λ)

Where:
- λ = expected goals per game
- PP effects and TOI effects are applied to λ, not probability

This immediately improved realism and interpretability.

---

## Phase 3 – Opportunity Modeling

A TOI-based opportunity proxy was added:

- TOI per game
- Team-relative TOI ratio
- Clamped multiplier (0.6 – 1.4)

This reduced overconfidence in low-usage players and improved ranking quality.

---

## Phase 4 – Power Play Reality (DailyFaceoff)

MoneyPuck PP inference was replaced with:
- DailyFaceoff scraped PP units (PP1 / PP2)

Key design decision:
- DailyFaceoff overrides MoneyPuck when available
- MoneyPuck acts as fallback only

This dramatically improved tactical realism.

---

## Phase 5 – Calibration Infrastructure

A full calibration pipeline was built:

- Daily prediction snapshots
- NHL API outcome collection
- Joined calibration datasets
- Brier score computation
- Reliability binning

This allowed **true probability evaluation**, not just ranking.

---

## Discovery – The Blocking Issue

Despite low Brier scores:
- All reliability bins showed 0% actual goals
- This was impossible and revealed a bug

Root cause:
❌ Goal attribution from NHL API was incomplete / incorrect  
✅ Probability math and feature engineering were sound

This was a **data-labeling failure**, not a modeling failure.

---

## Current State (End of Part 1)

### What Works
- Prediction model
- Poisson calibration
- TOI opportunity modeling
- Power-play integration
- End-to-end pipeline
- Historical backtests

### What Is Broken
- Actual goal scorer attribution from NHL API

---

## Key Insight

> Do not tune probabilities until outcomes are correct.

The project is now paused at the **exact right moment** to fix labeling,
before any further modeling complexity is added.

---

## What Comes Next (Part 2)

- Fix NHL goal attribution definitively
- Validate calibration properly
- Introduce odds-based EV selection
- Add controlled bet sizing
