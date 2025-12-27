# Next Steps – NHL Goal Scorer Project

## Immediate Priority (Single Focus)
Fix **actual goal scorer attribution**.

Until this is solved:
- Calibration curves are invalid
- Reliability analysis is meaningless
- Model tuning must stop

---

## What Needs Investigation

### NHL API Issues
- playerByGameStats structure
- Skater vs goalie separation
- Goal events vs summary totals
- playerId vs name vs abbreviation mismatches

### Matching Problems
- Name normalization inconsistencies
- Player traded / team mismatch edge cases
- Duplicate or missing player entries

---

## What NOT to Do Yet
❌ No probability tuning  
❌ No PP weighting changes  
❌ No TOI multiplier changes  

---

## Recommended Workflow
1. Open a **new focused project chat**
2. Provide Claude with:
   - CALIBRATION_RESULTS_2025-12.md
   - SESSION_LOG_NHL_SCORER_DEV.md
3. Ask Claude to:
   - Audit NHL API outcome extraction
   - Propose a robust scorer-identification method

Optionally:
- Ask Codex to help refactor the outcome collector once logic is clear

---

## Project Status
- Architecture: ✅ Complete
- Modeling: ✅ Stable
- Outcome attribution: ❌ Broken (blocking)
