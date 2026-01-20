# StandardCalculator `applies_to` Field Support - Discussion

**Date:** 2026-01-19  
**Status:** Deferred  
**Category:** Decision  
**Priority:** HIGH  
**Impact:** Score calculation inconsistency for asymmetric contests

---

## Problem Summary

The `StandardCalculator` (default time-series score calculator) does not respect the `applies_to` field in multiplier rules when calculating cumulative scores over time. This causes incorrect score calculations for asymmetric contests like ARRL DX, where different multiplier rules apply based on the operator's location type (W/VE vs DX).

---

## Issue Discovery

**Context:** ARRL DX contest implementation and multiplier breakdown report debugging.

**Symptom:**
- Plugin calculator (contest-specific) shows correct score (e.g., 30,843,750)
- `ScoreStatsAggregator` calculated score shows exactly half (e.g., 15,421,875)
- Score difference is exactly 2x, suggesting multiplier double-counting

**Root Cause:**
- ARRL DX has asymmetric multiplier rules:
  - W/VE operators: Only DXCC multipliers count (`applies_to: "W/VE"`)
  - DX operators: Only STPROV multipliers count (`applies_to: "DX"`)
- `ScoreStatsAggregator` correctly filters multiplier rules by `applies_to` (lines 168-171)
- `StandardCalculator` does NOT filter by `applies_to`, counting ALL multiplier rules
- For W/VE operators, `StandardCalculator` counts both DXCC (correct) and STPROV (incorrect), causing 2x multiplier count

---

## Architecture Discussion

### Why Does ARRL DX Use StandardCalculator?

ARRL DX has a contest-specific `scoring_module` (`arrl_dx_scoring`) for point calculation during log processing. However, ARRL DX does NOT have a `time_series_calculator` defined in its contest definition.

**Contest Definition Structure:**
- `scoring_module`: Python module for point calculation (ARRL DX has this: `arrl_dx_scoring`)
- `time_series_calculator`: Python module for cumulative score calculation over time (ARRL DX lacks this)

**Fallback Behavior:**
- When `time_series_calculator` is not specified, the system defaults to `StandardCalculator`
- `StandardCalculator` is the default time-series score calculator for all contests without custom calculators

**Result:**
- ARRL DX uses `arrl_dx_scoring` for point calculation (correct)
- ARRL DX uses `StandardCalculator` for time-series cumulative scores (incorrect for asymmetric contests)

---

## Plugin Architecture Boundary Discussion

### Initial Proposal

**Proposed Solution:** Add `applies_to` filtering to `StandardCalculator` to respect multiplier rule location type filtering.

**Reasoning:**
- `applies_to` is a declarative rule defined in contest definitions
- It's not contest-specific algorithmic logic
- Common declarative rules should be handled by core modules
- This ensures consistency across all calculators

### User Feedback

**Key Concern:** "The STANDARD CALCULATOR is only used when there isn't a plug-in for contest-specific scoring rules. Did your change potentially break the operation of the standard calculator for symmetric contests?"

**User Request:** Revert the change and discuss why ARRL DX, with a plug-in score calculator, is even referencing the standard calculator.

### Refined Architecture Principle

After discussion, the architectural principle was refined:

**Core Principle:** "Contest-specific algorithmic weirdness is implemented in code (plugins). Common declarative rules defined in contest definitions are handled by core modules."

**Boundary Definition:**
- **Plugins:** Handle contest-specific *algorithmic* logic (complex calculations, stateful logic, non-standard formulas)
- **Core Modules:** Handle *common declarative rules* defined in contest definitions (`applies_to` filtering, `totaling_method` variations, standard formulas)

**Implication:**
- `StandardCalculator` *should* handle `applies_to` filtering (it's a common declarative rule)
- This ensures all calculators (standard and contest-specific) respect the same declarative rules

---

## Proposed Solution

### Update StandardCalculator to Support `applies_to`

**File:** `contest_tools/score_calculators/standard_calculator.py`

**Change Required:**
- Add `applies_to` filtering in the multiplier calculation loop
- Filter multiplier rules based on `log_location_type` (from log metadata)
- Only process multiplier rules where `applies_to` is None or matches `log_location_type`

**Implementation Pattern:**
```python
# Filter multiplier rules by applies_to (similar to ScoreStatsAggregator)
log_location_type = getattr(log, '_my_location_type', None)
applicable_rules = [
    r for r in contest_def.multiplier_rules 
    if r.get('applies_to') is None or r.get('applies_to') == log_location_type
]

# Use applicable_rules instead of contest_def.multiplier_rules
for rule in applicable_rules:
    # ... multiplier calculation logic ...
```

**Existing Pattern:**
- `ScoreStatsAggregator` already implements this pattern (lines 168-171)
- `MultiplierStatsAggregator` already implements this pattern
- `TimeSeriesAggregator` already implements this pattern
- `StandardCalculator` is the only component that doesn't

---

## Risk Assessment

### Breaking Change Risk

**Risk Level:** MEDIUM

**Potential Impact:**
- Changing `StandardCalculator` affects ALL contests that use it (contests without custom `time_series_calculator`)
- Could break existing contests if implementation is incorrect
- Could cause regressions in score calculations

**Mitigation:**
- Comprehensive regression testing required
- Test all contest patterns (symmetric, asymmetric, different `totaling_method` values)
- Use existing regression test suite
- Compare `StandardCalculator` output with `ScoreStatsAggregator` output (golden reference)

### Contest Coverage

**Contests Using StandardCalculator:**
- ARRL 10 Meter (symmetric, `once_per_mode`)
- ARRL SS (symmetric, `once_per_log`)
- ARRL FD (symmetric, `once_per_mode`)
- CQ WW (symmetric, `sum_by_band`)
- CQ WPX (symmetric, `once_per_log`)
- IARU HF (symmetric, `sum_by_band`)
- CQ 160 (has `applies_to: W/VE` - may be affected)
- ARRL DX (asymmetric, `sum_by_band` - current issue)

**Contests with Custom Calculators:**
- WAE (has `wae_calculator`)
- NAQP (has `naqp_calculator`)
- ARRL DX (has `arrl_dx_scoring` for points, but not `time_series_calculator`)

---

## Testing Strategy

### Regression Testing Approach

**Golden Reference Pattern:**
- Use `ScoreStatsAggregator` as the source of truth
- `ScoreStatsAggregator` already correctly handles `applies_to` filtering
- Compare `StandardCalculator` output with `ScoreStatsAggregator` output
- Any differences indicate a bug in `StandardCalculator`

**Test Cases:**
1. **Symmetric Contests (Regression Tests):**
   - ARRL 10, ARRL SS, ARRL FD
   - CQ WW, CQ WPX, CQ 160
   - IARU HF
   - Verify scores match `ScoreStatsAggregator` (no changes expected)

2. **Asymmetric Contests (Fix Validation):**
   - ARRL DX CW/SSB (W/VE operator: DXCC only)
   - ARRL DX CW/SSB (DX operator: STPROV only)
   - Verify scores match `ScoreStatsAggregator` (fixes current 2x issue)

3. **Contests with `applies_to` Field:**
   - CQ 160 (has `applies_to: W/VE`)
   - Verify scores match `ScoreStatsAggregator`

4. **Different `totaling_method` Values:**
   - `once_per_log` (CQ WPX, ARRL SS)
   - `sum_by_band` (ARRL DX, NAQP, WAE, IARU HF)
   - `once_per_mode` (ARRL 10, ARRL FD)
   - `once_per_band_no_mode` (WRTC, CQ 160)

**Test Script:**
- See `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_TESTING_PLAN.md`

---

## Decision: Defer Implementation

**Status:** Deferred  
**Reason:** High risk of breaking changes requires comprehensive regression testing  
**Priority:** HIGH (affects score accuracy for asymmetric contests)

**Rationale:**
- This is a potentially breaking change affecting multiple contests
- Requires extensive regression testing before implementation
- Current workaround: Contest-specific plugins can override `StandardCalculator`
- For ARRL DX, the issue is mitigated because `ScoreStatsAggregator` uses the plugin calculator's score as authoritative

**Deferral Plan:**
1. Document the issue and solution approach
2. Create comprehensive test plan (completed)
3. When ready to implement:
   - Create test script with regression tests
   - Implement fix with `applies_to` filtering
   - Run full regression suite
   - Verify all test cases pass
   - Manual spot-checking with known good logs

---

## Related Files

- `contest_tools/score_calculators/standard_calculator.py` - File to be updated
- `contest_tools/data_aggregators/score_stats.py` - Reference implementation (lines 168-171)
- `contest_tools/data_aggregators/multiplier_stats.py` - Reference implementation
- `contest_tools/data_aggregators/time_series.py` - Reference implementation
- `DevNotes/Decisions_Architecture/PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md` - Architecture principle
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_TESTING_PLAN.md` - Testing plan
- `contest_tools/contest_definitions/arrl_dx_cw.json` - Example asymmetric contest definition

---

## Notes

- This issue was discovered during ARRL DX implementation and multiplier breakdown report debugging
- The 2x score difference was the key symptom that led to identifying this root cause
- `ScoreStatsAggregator` correctly uses the plugin calculator's score as authoritative, mitigating the impact
- However, time-series score calculations (used in animations and breakdown reports) still show incorrect values

---

**Last Updated:** 2026-01-19  
**Related Technical Debt:** See `TECHNICAL_DEBT.md` - "StandardCalculator `applies_to` Field Support"
