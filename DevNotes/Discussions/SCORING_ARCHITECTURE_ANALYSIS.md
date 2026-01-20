# Scoring Architecture and Single Source of Truth Analysis

## Summary

Analysis of scoring data inconsistencies across reports, considering contest-specific architecture requirements.

## Architecture Overview

### Two Types of Contest-Specific Scoring

**1. scoring_module** (Point Calculation)
- **Purpose**: Calculates `QSOPoints` column during log processing
- **Examples**: `arrl_10_scoring`, `arrl_dx_scoring`, `wae_scoring`
- **When Used**: During `apply_contest_specific_annotations()` (contest_log.py line 546-557)
- **Result**: Sets `df['QSOPoints']` in the DataFrame
- **Who Uses It**: 
  - ScoreStatsAggregator (reads `QSOPoints` column)
  - StandardCalculator (reads `QSOPoints` column)
  - All other aggregators that need points

**2. time_series_calculator** (Cumulative Score Calculation)
- **Purpose**: Calculates cumulative score over time for animations
- **Examples**: `wae_calculator`, `naqp_calculator`, `wrtc_calculator`
- **Default**: `standard_calculator` (if not specified)
- **When Used**: During `_pre_calculate_time_series_score()` (contest_log.py line 427-460)
- **Result**: Creates `log.time_series_score_df` with cumulative scores per time bin
- **Who Uses It**:
  - TimeSeriesAggregator (reads `time_series_score_df['score'].iloc[-1]` for final_score)

### Current Score Calculation Paths

**Path 1: ScoreStatsAggregator (Text Reports - CORRECT)**
```python
# score_stats.py
df_net = get_valid_dataframe(log, include_dupes=False)  # Already has QSOPoints from scoring_module
total_points = df_net['QSOPoints'].sum()
total_mults = calculate_multipliers(df_net, multiplier_rules)
final_score = total_points * total_mults  # (or other formula)
```

**Path 2: Score Calculator Plugin (Animation/Dashboard - INCORRECT)**
```python
# time_series.py line 235-238
if hasattr(log, 'time_series_score_df'):
    final_score = log.time_series_score_df['score'].iloc[-1]  # From calculator
```

### Contest-Specific Configuration

**ARRL 10 Meter Contest:**
```json
{
  "scoring_module": "arrl_10_scoring",  // ✓ Has contest-specific point calculation
  // No time_series_calculator specified  // Uses default standard_calculator
}
```

**Contests with Custom Calculators:**
- WAE: `time_series_calculator: "wae_calculator"`
- NAQP: `time_series_calculator: "naqp_calculator"`
- WRTC: `time_series_calculator: "wrtc_calculator"`

**Contests with scoring_module but NO custom calculator:**
- ARRL 10: `scoring_module: "arrl_10_scoring"` → uses `standard_calculator`
- ARRL DX: `scoring_module: "arrl_dx_scoring"` → uses `standard_calculator`
- ARRL SS: `scoring_module: "arrl_ss_scoring"` → uses `standard_calculator`
- CQ WW: `scoring_module: "cq_ww_scoring"` → uses `standard_calculator`
- Most other contests

## The Problem

### Why Scores Differ

1. **Multiplier Calculation Differences**
   - ScoreStatsAggregator: Uses contest rules (`totaling_method`, `once_per_mode`, etc.)
   - StandardCalculator: May calculate multipliers differently during time-series accumulation
   - Result: Different multiplier totals → Different final scores

2. **Timing/Ordering Differences**
   - ScoreStatsAggregator: Calculates from final totals (all QSOs)
   - StandardCalculator: Calculates cumulatively per time bin (may have intermediate rounding/accumulation errors)

3. **Data Filtering Differences**
   - ScoreStatsAggregator: Uses `include_dupes=False` (excludes dupes)
   - StandardCalculator: Also uses `df_non_dupes`, but may handle edge cases differently

### Evidence

Both paths start with the same data:
- Both use `QSOPoints` from `scoring_module` ✓
- Both exclude dupes ✓
- But they calculate multipliers and final score differently ✗

## Architecture Principle

**"Contest-specific weirdness is implemented in code"**

This means:
1. Contest-specific scoring logic belongs in:
   - `scoring_module` for point calculation
   - `time_series_calculator` for cumulative score calculation
2. Standard/generic logic uses default implementations
3. Aggregators should respect contest-specific plugins

## Proposed Solution Analysis

### Option 1: Make ScoreStatsAggregator the Single Source (PROBLEMATIC)

**Problem:**
- Violates architecture principle
- Ignores contest-specific `time_series_calculator` plugins
- Would break WAE, NAQP, WRTC which have custom calculators
- StandardCalculator might be correct for some contests

**Why it doesn't fit:**
- ARRL 10 uses `standard_calculator` (which should be correct)
- If `standard_calculator` is wrong, it should be fixed, not bypassed
- Contests with custom calculators (WAE, NAQP, WRTC) expect their calculator to be authoritative

### Option 2: Fix StandardCalculator to Match ScoreStatsAggregator (RECOMMENDED)

**Why:**
- Respects architecture: Calculator is the contest-specific implementation
- Keeps contest-specific logic in plugins
- Ensures calculator and aggregator match

**Implementation:**
1. Fix `standard_calculator` to use same multiplier logic as ScoreStatsAggregator
2. Ensure final score calculation matches
3. Use calculator's final score as single source of truth

**Changes Needed:**
- `standard_calculator.py`: Align multiplier calculation with ScoreStatsAggregator
- Use same `totaling_method` logic
- Use same multiplier filtering rules

### Option 3: Make ScoreStatsAggregator Use Calculator for Final Score (BETTER)

**Why:**
- Calculator is the contest-specific "plugin" (per architecture principle)
- Respects custom calculators (WAE, NAQP, WRTC)
- Single source: Calculator's final score

**Implementation:**
1. ScoreStatsAggregator: Use calculator's final score if available
2. Fallback to direct calculation if calculator not available
3. Both paths converge on calculator as source of truth

**Changes Needed:**
- `score_stats.py`: Use `log.time_series_score_df['score'].iloc[-1]` if available
- Keep direct calculation as fallback/validation

### Option 4: Validation/Reconciliation Approach (SAFEST)

**Why:**
- Doesn't break existing architecture
- Identifies discrepancies
- Allows gradual migration

**Implementation:**
1. TimeSeriesAggregator: Continue using calculator
2. ScoreStatsAggregator: Calculate directly
3. Add validation: Warn if they don't match
4. Use calculator as authoritative source

## Recommendation: Option 3 + Option 4 Hybrid

**Make Calculator the Single Source, but with validation:**

1. **TimeSeriesAggregator** (Animation/Dashboard):
   - Continue using calculator's final score ✓ (already correct architecture)

2. **ScoreStatsAggregator** (Text Reports):
   - Use calculator's final score if available (respects contest-specific plugin)
   - Fallback to direct calculation if calculator not available
   - Add validation warning if they differ

3. **Fix StandardCalculator**:
   - Ensure multiplier calculation matches ScoreStatsAggregator's logic
   - Use same `totaling_method` rules
   - This fixes the root cause for ARRL 10 and other contests using `standard_calculator`

## Impact Analysis

### Contests Affected

**Contests using `standard_calculator`:**
- ARRL 10 (affected)
- ARRL DX (potentially affected)
- ARRL SS (potentially affected)
- CQ WW (potentially affected)
- Most other contests (potentially affected)

**Contests with custom calculators:**
- WAE (`wae_calculator`) - likely not affected (has its own logic)
- NAQP (`naqp_calculator`) - likely not affected (has its own logic)
- WRTC (`wrtc_calculator`) - likely not affected (has its own logic)

### Reports Affected

**Using ScoreStatsAggregator:**
- `text_score_report` (correct score)
- `text_comparative_score_report` (correct score)

**Using TimeSeriesAggregator:**
- `plot_interactive_animation` (incorrect score) ✓ FIXED BY ALIGNING CALCULATOR
- Dashboard scoreboard (incorrect score) ✓ FIXED BY ALIGNING CALCULATOR

## Conclusion

**The fix should:**
1. Make the calculator (plugin) the single source of truth for final score
2. Fix `standard_calculator` to match ScoreStatsAggregator's multiplier logic
3. Have ScoreStatsAggregator use calculator's score when available
4. Maintain architecture: "Contest-specific weirdness in code" (plugins/calculators)

This ensures:
- ARRL 10 (and other standard contests) use correct calculator
- WAE, NAQP, WRTC continue using their custom calculators
- All reports/dashboards show the same score
- Architecture principle is respected
