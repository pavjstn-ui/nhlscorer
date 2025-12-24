# OddsAPI NHL Goal Scorer Data - Debugging Guide

## Problem
OddsAPI is not returning NHL goal scorer data when using EU market setup.

## Root Cause
**EU bookmakers have very limited NHL coverage** - hockey isn't popular in Europe, so most EU markets won't have NHL player props (anytime goal scorer odds).

---

## Quick Fix: Switch to USA Markets

Use USA/North American bookmakers in OddsAPI where NHL is popular:
- Better player prop coverage (anytime goal scorer, over/under goals, etc.)
- More bookmakers offering these markets
- More competitive odds

**Common USA books:** FanDuel, DraftKings, BetMGM, Caesars

---

## Debugging Steps

### 1. Check Your Endpoint Structure

**Correct OddsAPI player props endpoint:**
```python
# Step 1: Get list of upcoming NHL events
GET https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds
?apiKey=YOUR_KEY
&regions=us  # <-- CHANGE FROM 'eu' TO 'us'
&markets=player_goal_scorer

# OR try this market name:
&markets=player_anytime_goalscorer
```

### 2. Common Mistakes to Check

- ❌ Using `h2h` market instead of player props market
- ❌ Using `regions=eu` instead of `regions=us`
- ❌ Not getting event IDs first before querying player props
- ❌ Free tier limitations (player props might require paid tier)

### 3. Test Directly in Browser

Copy this URL (replace YOUR_KEY):
```
https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds?apiKey=YOUR_KEY&regions=us&markets=player_goal_scorer
```

If it returns empty data, try:
```
https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds?apiKey=YOUR_KEY&regions=us&markets=player_anytime_goalscorer
```

### 4. Python Code Template

```python
import requests

API_KEY = 'your_key_here'
SPORT = 'icehockey_nhl'
REGIONS = 'us'  # Changed from 'eu'
MARKETS = 'player_goal_scorer'

# Get NHL events with player props
url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
params = {
    'apiKey': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS
}

response = requests.get(url, params=params)
print(f"Status Code: {response.status_code}")
print(f"Remaining Requests: {response.headers.get('x-requests-remaining')}")
print(f"Response: {response.json()}")
```

---

## Alternative Data Sources

### For NHL Stats (Free)
1. **NHL Official API** (Best free option)
   - `https://api-web.nhle.com/v1/`
   - Player stats, game data, historical records
   - No auth required

2. **Natural Stat Trick** - Advanced analytics
   - Can scrape or use data exports
   - Expected goals, shot quality metrics

3. **Hockey Reference** - Comprehensive stats
   - Scrapeable (respect rate limits)
   - Historical data back decades

### For Odds Data (Paid)
1. **OddsAPI** (current) - $50-200/month depending on calls
2. **SportRadar** - Professional grade, expensive
3. **BetQL/OddsJam APIs** - Mid-tier pricing

---

## Recommended Approach

**Start with: OddsAPI (USA markets) + NHL Official API**
- Free/low-cost combo to validate model
- OddsAPI for odds data
- NHL API for stats/features
- Only upgrade to paid stats if needed

---

## Next Steps

1. Update your code to use `regions=us` instead of `regions=eu`
2. Verify the correct market name (`player_goal_scorer` vs `player_anytime_goalscorer`)
3. Test the endpoint in browser first to confirm data is available
4. Check OddsAPI documentation for exact market names: https://the-odds-api.com/liveapi/guides/v4/
5. If still failing, check if your API tier supports player props

---

## If Still Not Working

**Bring the following information:**
- Exact error message or empty response
- API endpoint URL you're using
- Response status code
- Your OddsAPI tier (free/paid)
- Sample of the response JSON (even if empty)

This will help diagnose the exact issue quickly.
