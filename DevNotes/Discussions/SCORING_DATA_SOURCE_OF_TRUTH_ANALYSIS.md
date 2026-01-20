# Scoring Data Source of Truth Analysis

## Problem Summary

There is a scoring inconsistency across different components:
- **Text score reports** (`score_report_VP2VMM.txt`): Show **correct** score
- **Animation racing bar**: Shows **lower** (incorrect) score
- **Dashboard scoreboard**: Shows **wrong** (incorrect) score

All components should use the same source of truth for scoring data.

## Current State Analysis

### 1. Text Score Report (CORRECT) - Uses ScoreStatsAggregator

**Location:** `contest_tools/reports/text_score_report.py`

**Score Source:**
```python
# Line 57-63
aggregator = ScoreStatsAggregator([log])
all_scores = aggregator.get_score_breakdown()
final_score = log_scores['final_score']  # From ScoreStatsAggregator
```

**How it calculates:**
- Uses `ScoreStatsAggregator.get_score_breakdown()`
- Calculates score directly from data: `Points * Multipliers` (or `QSOs * Multipliers`, etc.)
- Implementation: `contest_tools/data_aggregators/score_stats.py` lines 160-166
- Formula based on `contest_def.score_formula`:
  - `qsos_times_mults`: `QSOs * total_multiplier_count`
  - `total_points`: `Points` (no multipliers)
  - `points_times_mults`: `Points * total_multiplier_count` (default)

### 2. Animation (INCORRECT) - Uses TimeSeriesAggregator

**Location:** `contest_tools/reports/plot_interactive_animation.py`

**Score Source:**
```python
# Lines 608-621 (band) or 732-741 (mode)
ts_raw = get_cached_ts_data()  # or TimeSeriesAggregator(self.logs).get_time_series_data()
log_entry = ts_raw['logs'][call]
if any(log_entry['cumulative']['score']):
    metric = log_entry['cumulative']['score']
ts_data[call] = {'score': metric}
```

**How it gets score:**
- Uses `TimeSeriesAggregator.get_time_series_data()`
- Gets cumulative score from `log.time_series_score_df` (line 235-244 in time_series.py)
- This is calculated by the **score calculator plugin** (StandardCalculator, NaqpCalculator, etc.)

### 3. Dashboard Scoreboard (INCORRECT) - Uses TimeSeriesAggregator

**Location:** `web_app/analyzer/views.py`

**Score Source:**
```python
# Lines 442-444, 523-526
ts_agg = TimeSeriesAggregator(lm.logs)
ts_data = ts_agg.get_time_series_data()
# ...
'score': data['scalars'].get('final_score', 0)  # From TimeSeriesAggregator
```

**How it gets score:**
- Uses `TimeSeriesAggregator.get_time_series_data()`
- Gets `final_score` from `log.time_series_score_df['score'].iloc[-1]` (line 238 in time_series.py)
- Same source as animation - from score calculator plugin

## Root Cause

### Two Different Score Calculation Paths

**Path 1: ScoreStatsAggregator (Correct)**
- Calculates score directly from DataFrame
- Uses contest definition rules (score_formula, multiplier_rules)
- Implementation: `score_stats.py` `_calculate_log_score()` method
- Used by: Text score reports

**Path 2: Score Calculator Plugin (Incorrect/Outdated)**
- Calculates score via time series calculation
- Creates `log.time_series_score_df` with cumulative score per time bin
- Implementation: `score_calculators/standard_calculator.py`, `naqp_calculator.py`, etc.
- Used by: Animation, Dashboard (via TimeSeriesAggregator)

### The Problem

The score calculator plugin and ScoreStatsAggregator may calculate scores differently:
1. **Different data sources**: Calculator may use different DataFrame filtering
2. **Different multiplier logic**: Calculator may have outdated multiplier totaling rules
3. **Different timing**: Calculator calculates per time bin, ScoreStatsAggregator calculates final totals
4. **Calculation order**: Differences in when multipliers are calculated vs. when score is computed

### Evidence

**TimeSeriesAggregator uses cached calculator data:**
```python
# time_series.py line 235-238
if not is_filtered and hasattr(log, 'time_series_score_df') and log.time_series_score_df is not None:
    # Extract final score for scalars
    if not log.time_series_score_df.empty and 'score' in log.time_series_score_df.columns:
        log_entry["scalars"]["final_score"] = int(log.time_series_score_df['score'].iloc[-1])
```

**ScoreStatsAggregator calculates independently:**
```python
# score_stats.py lines 160-166
if contest_def.score_formula == 'qsos_times_mults':
    final_score = total_summary['QSOs'] * total_multiplier_count
elif contest_def.score_formula == 'total_points':
    final_score = total_summary['Points']
else: # Default to points_times_mults
    final_score = total_summary['Points'] * total_multiplier_count
```

## Solution Requirements

### Single Source of Truth

The user wants:
- **One source of truth**: The "plug-in" (score calculator)
- **DAL usage**: Both score report and animation/dashboard should use the same DAL component
- **Consistency**: All components show the same score

### The "Plug-In" Reference

The "plug-in" refers to the **contest-specific score calculator**:
- `StandardCalculator` (standard contests)
- `NaqpCalculator` (NAQP contests)
- `WaeCalculator` (WAE contests)
- These calculate `log.time_series_score_df` with cumulative scores

However, these calculators may be outdated or calculate scores differently than ScoreStatsAggregator.

## Recommended Solution

### Option 1: Make ScoreStatsAggregator the Single Source of Truth (Recommended)

**Why:**
- ScoreStatsAggregator is already correct (text reports work)
- It directly implements contest definition rules
- It's in the DAL (Data Aggregation Layer)
- Easier to maintain one calculation path

**Changes:**
1. **TimeSeriesAggregator**: Use ScoreStatsAggregator for `final_score` instead of `time_series_score_df`
2. **Animation**: Already uses TimeSeriesAggregator, will automatically get correct score
3. **Dashboard**: Already uses TimeSeriesAggregator, will automatically get correct score

**Implementation:**
```python
# In time_series.py, replace line 235-238 with:
# Use ScoreStatsAggregator as single source of truth for final_score
from ..data_aggregators.score_stats import ScoreStatsAggregator
if not is_filtered:
    score_agg = ScoreStatsAggregator([log])
    score_data = score_agg.get_score_breakdown()
    log_entry["scalars"]["final_score"] = score_data["logs"].get(call, {}).get('final_score', 0)
```

**Keep calculator for time series (cumulative score over time):**
- Still use `time_series_score_df` for cumulative score arrays (animation progression)
- But use ScoreStatsAggregator for final score scalar (single number)

### Option 2: Make Score Calculator Match ScoreStatsAggregator

**Why:**
- Preserves existing architecture
- Calculator would be the single source

**Changes:**
1. Update score calculators to match ScoreStatsAggregator logic
2. Ensure multiplier calculations match
3. Ensure score formulas match

**Downside:**
- More complex (multiple calculators to update)
- Risk of divergence if calculators aren't kept in sync
- ScoreStatsAggregator is already proven correct

### Option 3: Hybrid Approach

**Use ScoreStatsAggregator for final_score, Calculator for cumulative arrays:**

- **Final Score Scalar**: Always from ScoreStatsAggregator (for dashboard, text reports)
- **Cumulative Score Array**: From calculator (for animation progression over time)
- **Validation**: Ensure calculator's final value matches ScoreStatsAggregator's final_score

**Implementation:**
- TimeSeriesAggregator uses ScoreStatsAggregator for `scalars['final_score']`
- TimeSeriesAggregator uses `time_series_score_df` for `cumulative['score']` array
- Add validation check: `assert calculator_final == aggregator_final`

## Implementation Details

### Where Changes Are Needed

1. **TimeSeriesAggregator** (`contest_tools/data_aggregators/time_series.py`):
   - Lines 235-238: Replace `time_series_score_df['score'].iloc[-1]` with ScoreStatsAggregator

2. **Animation Report** (`contest_tools/reports/plot_interactive_animation.py`):
   - Already uses TimeSeriesAggregator - no changes needed
   - Will automatically get correct score after TimeSeriesAggregator fix

3. **Dashboard** (`web_app/analyzer/views.py`):
   - Already uses TimeSeriesAggregator - no changes needed
   - Will automatically get correct score after TimeSeriesAggregator fix

4. **Score Report** (`contest_tools/reports/text_score_report.py`):
   - Already uses ScoreStatsAggregator - no changes needed

### Validation

After fix:
- All components should show the same final score
- Text reports: Use ScoreStatsAggregator (unchanged)
- Animation: Use TimeSeriesAggregator (which now uses ScoreStatsAggregator)
- Dashboard: Use TimeSeriesAggregator (which now uses ScoreStatsAggregator)

## Conclusion

**Recommended Solution: Option 1 (Make ScoreStatsAggregator the Single Source of Truth)**

- ScoreStatsAggregator is already correct and in the DAL
- All components can use it via TimeSeriesAggregator
- Maintains architecture (DAL pattern)
- Minimal code changes required
- Ensures consistency across all reports and dashboards
