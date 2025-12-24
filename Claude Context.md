# NHLScorer — Claude Context (Authoritative)

Repository:
https://github.com/pavjstn-ui/nhlscorer.git

This file defines the CURRENT STATE of the project.
Claude should treat this as FIXED CONTEXT unless explicitly told otherwise.

---

## 1. Project Goal (Locked)

Build a **simple, fast NHL goal-scorer analysis tool**.

Purpose:
- Identify **likely goal scorers for upcoming NHL games**
- Use **historical stats + matchup context**
- Produce a **ranked list**
- Human manually decides & places bets

This is NOT:
- an auto-betting system
- a live trading bot
- a deep ML / RL system (yet)

---

## 2. Scope Decisions (Already Made)

### Included
- NHL only
- Player goal scoring focus
- Daily batch analysis
- Historical data first
- Notebook-driven exploration
- Simple Python scripts for ingestion & ranking

### Explicitly Excluded (for now)
- Reinforcement learning
- Neural networks
- Live betting execution
- Over-engineered pipelines
- Multi-sport abstractions

Do NOT re-suggest these unless asked.

---

## 3. Data Situation (Current Reality)

### Odds
- The Odds API tested
- Working markets:
  - h2h
  - totals
  - spreads
- ❌ Player goal scorer markets NOT supported on current endpoint

Decision:
- Use odds for **game context only**
- Goal scorer odds to be revisited later (new provider or upgrade)

### Stats
Using / planning to use:
- NHL player stats (goals, shots, ice time)
- Team defensive stats
- Goalie performance
- Power-play usage

Historical data first. No live feed dependency.

---

## 4. Repository Philosophy

This repo is:
- Small
- Focused
- Iterative
- Notebook-friendly

Claude should:
- Extend, not redesign
- Add files incrementally
- Avoid speculative architecture

---

## 5. Intended Workflow

1. Load historical NHL data
2. Explore patterns in notebooks
3. Define simple scoring heuristics
4. Rank players per game day
5. Output shortlist (top ~20–30, narrowed to 3–6)

Baseline logic first.
ML only after baseline proves useful.

---

## 6. Coding Rules

- Clear filenames
- Readable Python
- No premature optimization
- No “frameworks”
- Markdown explanations preferred
- Each script does ONE thing

---

## 7. Git Expectations

- Small commits
- Logical units
- No broken notebooks
- Data files handled deliberately (ignored or documented)

---

## 8. Tone & Behavior Expected From Claude

Claude should:
- Assume the author knows what they’re doing
- Not re-teach Python basics
- Not restart planning from scratch
- Ask before changing direction
- Respect decisions already made

---

## 9. Open Questions (Parked)

These are NOT blockers:
- Best scorer-odds provider
- Paid Odds API tier
- Scraping bookmakers
- ML ranking models

Only revisit when explicitly requested.

---

## End of Context
