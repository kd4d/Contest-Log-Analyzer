# StandardCalculator `applies_to` Field Support - Implementation Plan

**Date:** 2026-01-20  
**Status:** Ready for Implementation  
**Priority:** HIGH  
**Category:** Architecture & Design Debt

---

## Executive Summary

This plan implements `applies_to` field filtering in `StandardCalculator` to fix incorrect score calculations for asymmetric contests (e.g., ARRL DX). The change ensures `StandardCalculator` respects multiplier rule location type filtering, aligning it with other aggregators (`ScoreStatsAggregator`, `MultiplierStatsAggregator`, `TimeSeriesAggregator`).

**Expected Outcome:**
- ✅ Fixes 2x multiplier counting issue for ARRL DX (W/VE and DX operators)
- ✅ No regressions for symmetric contests (backward compatible)
- ✅ Consistent behavior across all score calculation components

---

## Problem Statement

### Current Issue

**Symptom:**
- ARRL DX W/VE operators: Plugin calculator shows correct score (e.g., 30,843,750)
- `StandardCalculator` shows exactly half (e.g., 15,421,875) - 2x multiplier count
- ARRL DX DX operators: Same 2x issue (opposite multiplier rule)

**Root Cause:**
- `StandardCalculator` processes ALL multiplier rules without filtering by `applies_to`
- ARRL DX has asymmetric rules:
  - W/VE operators: Only DXCC multipliers count (`applies_to: "W/VE"`)
  - DX operators: Only STPROV multipliers count (`applies_to: "DX"`)
- `StandardCalculator` counts both rules → 2x multiplier count → 2x score

**Affected Contests:**
- ARRL DX CW/SSB (primary issue)
- CQ 160 (has `applies_to: "W/VE"` - needs validation)
- Any future asymmetric contests using `StandardCalculator`

---

## Solution Design

### Implementation Pattern

**Reference Implementation:** `ScoreStatsAggregator` (lines 176-179 in `score_stats.py`)

```python
applies_to = rule.get('applies_to')
if applies_to and log_location_type and applies_to != log_location_type:
    # Skip this rule - doesn't apply to this operator's location type
    continue
```

**StandardCalculator Change:**
- Add location type retrieval at start of `calculate()` method
- Filter multiplier rules by `applies_to` before processing
- Only process rules where `applies_to` is None or matches `log_location_type`

### Code Changes

**File:** `contest_tools/score_calculators/standard_calculator.py`

**Location:** Line ~47 (after multiplier_columns extraction, before multiplier rule loop)

**Change:**
1. Extract `log_location_type` from log object
2. Filter `multiplier_rules` to only applicable rules
3. Use filtered rules in all multiplier calculation loops

**Implementation:**
```python
# After line 47 (multiplier_columns extraction)
# --- Filter Multiplier Rules by applies_to ---
log_location_type = getattr(log, '_my_location_type', None)
applicable_multiplier_rules = [
    rule for rule in log.contest_definition.multiplier_rules
    if rule.get('applies_to') is None or rule.get('applies_to') == log_location_type
]

# Update multiplier_columns to only include applicable rules
multiplier_columns = sorted(list(set([
    rule['value_column'] for rule in applicable_multiplier_rules
])))

# ... existing df_for_mults filtering logic ...

# Change line 83: Use applicable_multiplier_rules instead of log.contest_definition.multiplier_rules
for rule in applicable_multiplier_rules:
    # ... existing multiplier calculation logic ...
```

### Backward Compatibility

**Symmetric Contests (No `applies_to`):**
- All multiplier rules have `applies_to: null` or no `applies_to` field
- Filtering logic: `if None or None == log_location_type` → Always True
- Result: All rules processed (no change in behavior)

**Asymmetric Contests (With `applies_to`):**
- Rules have `applies_to: "W/VE"` or `applies_to: "DX"`
- Filtering logic: Only matching rules processed
- Result: Correct multiplier counting (fixes 2x issue)

**Edge Case: Location Type Not Set:**
- If `log_location_type` is None and rule has `applies_to`:
  - Filter: `if applies_to and None and applies_to != None` → False
  - Result: Rule is skipped (safe default - better than double-counting)

---

## Testing Strategy

### Test Framework

**Golden Reference:** `ScoreStatsAggregator`
- Already correctly handles `applies_to` filtering
- Calculates final score from totals (not time-series)
- Use as source of truth for comparison

**Test Approach:**
1. Process log through both `StandardCalculator` and `ScoreStatsAggregator`
2. Compare final scores and multiplier counts
3. Assert they match (within tolerance for time-series rounding)

### Test Categories

#### 1. Regression Tests (Symmetric Contests)

**Objective:** Verify no changes for contests without `applies_to` rules

**Test Cases:**
- ARRL 10 Meter (`once_per_mode`, no `applies_to`)
- ARRL SS (`once_per_log`, no `applies_to`)
- ARRL FD (`once_per_mode`, no `applies_to`)
- CQ WW CW/SSB/RTTY (`sum_by_band`, no `applies_to`)
- CQ WPX CW/SSB (`once_per_log`, no `applies_to`)
- IARU HF (`sum_by_band`, no `applies_to`)

**Expected:** Scores identical before/after change (no filtering happens)

**Test Logs:**
- Use existing logs from `regressiontest.bat`
- CQ WW: k3lr, w3lpl, k1lz
- ARRL SS: kd4d, k3mm, aa3b
- CQ WPX: k3lr, kc1xx, ni4w, kb4dx
- ARRL 10: ve3ej, vp2vmm
- ARRL FD: w1op, w3ao
- IARU HF: nn3w, n9nb, gb5wr, gb9wr

#### 2. Fix Validation Tests (ARRL DX)

**Objective:** Verify fix works for asymmetric contests

**Test Cases:**
- ARRL DX CW - W/VE operator (should count DXCC only)
- ARRL DX CW - DX operator (should count STPROV only)
- ARRL DX SSB - W/VE operator (should count DXCC only)
- ARRL DX SSB - DX operator (should count STPROV only)

**Expected:**
- Before change: 2x scores (both rules counted)
- After change: Correct scores (only applicable rule counted)
- Final score matches `ScoreStatsAggregator` (within ±1 point tolerance)

**Test Logs:**
- ARRL DX CW: k5zd (W/VE), aa3b (W/VE), 8p5a (DX - Barbados), p44w (DX - Aruba)
- ARRL DX SSB: 8p5a (DX), zf1a (DX - Cayman Islands)
- Need to verify location types are correctly set

#### 3. Edge Case Tests

**Test Cases:**
- Contest with `applies_to` but `log_location_type` not set (None)
- Contest with mixed rules (some with `applies_to`, some without)
- CQ 160 with `applies_to: "W/VE"` (if applicable)

**Expected:**
- Location type not set: Rules with `applies_to` are skipped (safe default)
- Mixed rules: Rules without `applies_to` always processed, rules with `applies_to` filtered
- CQ 160: Score matches `ScoreStatsAggregator`

#### 4. Comprehensive Pattern Tests

**Test Cases:**
- All `totaling_method` values with `applies_to`:
  - `sum_by_band` with `applies_to` (ARRL DX)
  - `once_per_log` with `applies_to` (if any exist)
  - `once_per_mode` with `applies_to` (if any exist)
  - `once_per_band_no_mode` with `applies_to` (CQ 160)

**Expected:** All patterns produce correct results

### Test Script Structure

**File:** `test_code/test_standard_calculator_applies_to.py`

**Test Class:**
```python
class TestStandardCalculatorAppliesTo:
    """Test StandardCalculator applies_to filtering and regression tests."""
    
    def test_symmetric_contests_no_regression(self):
        """Test that symmetric contests (no applies_to) are unchanged."""
        # Test: ARRL 10, ARRL SS, CQ WW, CQ WPX, IARU HF, ARRL FD
        # Assert: Scores identical before/after change
        
    def test_arrl_dx_w_ve_operator(self):
        """Test ARRL DX with W/VE operator (should count DXCC only)."""
        # Test: W/VE operator log
        # Assert: Score matches ScoreStatsAggregator
        # Assert: Multiplier count = DXCC count only
        
    def test_arrl_dx_dx_operator(self):
        """Test ARRL DX with DX operator (should count STPROV only)."""
        # Test: DX operator log
        # Assert: Score matches ScoreStatsAggregator
        # Assert: Multiplier count = STPROV count only
        
    def test_cq_160_with_applies_to(self):
        """Test CQ 160 contest with applies_to filtering."""
        # Test: CQ 160 log (has applies_to: W/VE)
        # Assert: Score matches ScoreStatsAggregator
        
    def test_all_totaling_methods_with_applies_to(self):
        """Test all totaling_method patterns with applies_to."""
        # Test: sum_by_band, once_per_log, once_per_mode, etc.
        # Assert: All produce correct results
        
    def test_mixed_rules(self):
        """Test contest with mixed rules (some with applies_to, some without)."""
        # Edge case: Multiple multiplier rules, some filtered, some not
        
    def test_location_type_not_set(self):
        """Test behavior when applies_to exists but location type not determined."""
        # Edge case: Should skip rules with applies_to when location type is None
```

### Comparison Logic

**Tolerance:**
- **Scores:** ±1 point difference allowed (time-series rounding)
- **Multipliers:** Must match exactly (no rounding in multiplier counting)

**Comparison Function:**
```python
def compare_calculators(log, tolerance=1):
    """Compare StandardCalculator vs ScoreStatsAggregator."""
    # Process both
    score_agg = ScoreStatsAggregator([log])
    score_agg_result = score_agg.get_score_breakdown()
    
    calculator = StandardCalculator()
    df_non_dupes = log.get_processed_data()[log.get_processed_data()['Dupe'] == False]
    calculator_result = calculator.calculate(log, df_non_dupes)
    
    # Extract metrics
    callsign = log.get_metadata().get('MyCall', 'Unknown')
    reference = score_agg_result['logs'][callsign]
    calculator_score = int(calculator_result['score'].iloc[-1])
    calculator_mults = int(calculator_result['total_mults'].iloc[-1])
    
    # Compare
    errors = []
    score_diff = abs(calculator_score - reference['final_score'])
    if score_diff > tolerance:
        errors.append(f"Score mismatch: {calculator_score:,} vs {reference['final_score']:,} (diff: {score_diff:,})")
    
    # Multiplier comparison (extract from reference)
    reference_total_mults = sum([
        reference['total_summary'].get(rule['name'], 0)
        for rule in log.contest_definition.multiplier_rules
        if rule.get('applies_to') is None or rule.get('applies_to') == getattr(log, '_my_location_type', None)
    ])
    
    if calculator_mults != reference_total_mults:
        errors.append(f"Multiplier mismatch: {calculator_mults} vs {reference_total_mults}")
    
    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'metrics': {
            'calculator_score': calculator_score,
            'reference_score': reference['final_score'],
            'calculator_mults': calculator_mults,
            'reference_mults': reference_total_mults
        }
    }
```

---

## Implementation Steps

### Phase 1: Create Test Script (Before Changes)

**Objective:** Establish baseline and golden reference

1. **Create test script structure**
   - File: `test_code/test_standard_calculator_applies_to.py`
   - Implement test class with all test methods
   - Use existing test logs from `regressiontest.bat`

2. **Run baseline tests** (using current StandardCalculator)
   - Run all test cases
   - Capture baseline results
   - Document expected vs actual for ARRL DX (confirms the bug)
   - Verify symmetric contests match ScoreStatsAggregator

3. **Establish golden reference**
   - Use ScoreStatsAggregator as truth
   - Verify all symmetric contests match
   - Document ARRL DX mismatch (2x issue confirmed)

**Deliverable:** Test script with baseline results showing ARRL DX failures

### Phase 2: Implement Code Change

**Objective:** Add `applies_to` filtering to StandardCalculator

1. **Update StandardCalculator**
   - File: `contest_tools/score_calculators/standard_calculator.py`
   - Add location type extraction (after line 47)
   - Filter multiplier rules by `applies_to`
   - Update multiplier_columns extraction
   - Change loop to use filtered rules (line 83)

2. **Code Review Checklist**
   - [ ] Logic matches ScoreStatsAggregator pattern
   - [ ] Backward compatible (symmetric contests unchanged)
   - [ ] Edge cases handled (location type None)
   - [ ] No side effects on other code paths
   - [ ] Docstring updated if needed

**Deliverable:** Updated StandardCalculator with `applies_to` filtering

### Phase 3: Validate Changes

**Objective:** Verify fix works and no regressions

1. **Run full test suite**
   ```bash
   python test_code/test_standard_calculator_applies_to.py
   ```

2. **Verify Results**
   - ✅ All symmetric contests: No change (regression tests pass)
   - ✅ ARRL DX W/VE: Correct scores (DXCC only, matches ScoreStatsAggregator)
   - ✅ ARRL DX DX: Correct scores (STPROV only, matches ScoreStatsAggregator)
   - ✅ CQ 160: Correct scores (if applicable)
   - ✅ All `totaling_method` patterns work correctly

3. **Manual Verification**
   - Run `regressiontest.bat` to ensure no unexpected regressions
   - Spot-check a few contest reports visually
   - Verify ARRL DX reports show correct scores

4. **Document Results**
   - Update test results
   - Document any edge cases discovered
   - Note any tolerance thresholds needed
   - Update TECHNICAL_DEBT.md (mark as completed)

**Deliverable:** All tests passing, no regressions, fix validated

---

## Risk Assessment & Mitigation

### Risk 1: Breaking Symmetric Contests

**Risk Level:** LOW  
**Mitigation:**
- `applies_to` filtering only activates when rule has `applies_to` field
- Symmetric contests have no `applies_to` → no filtering happens
- Test all symmetric contests in regression suite
- Backward compatible by design

### Risk 2: Location Type Not Set

**Risk Level:** LOW  
**Mitigation:**
- Check if `log_location_type` is None or empty
- If no location type: Rules with `applies_to` are skipped (safe default)
- Better than double-counting (current bug)
- Add test case for this scenario

### Risk 3: Time-Series Accumulation Differences

**Risk Level:** LOW  
**Mitigation:**
- Use ScoreStatsAggregator as reference (calculates from final totals)
- StandardCalculator uses time-series (may have minor rounding)
- Allow ±1 point tolerance for legitimate differences
- Document tolerance in test results

### Risk 4: Multiplier Column Extraction

**Risk Level:** MEDIUM  
**Mitigation:**
- Must update `multiplier_columns` extraction to use filtered rules
- Otherwise, columns from filtered-out rules still processed
- Test with ARRL DX to verify only applicable columns processed

---

## Success Criteria

### Must Pass (Blocking)

1. ✅ All symmetric contests: Scores unchanged (regression tests)
2. ✅ ARRL DX W/VE: Score matches ScoreStatsAggregator (within ±1 tolerance)
3. ✅ ARRL DX DX: Score matches ScoreStatsAggregator (within ±1 tolerance)
4. ✅ Multiplier counts match exactly (no rounding differences)
5. ✅ No new warnings in regression test output

### Should Pass (Non-Blocking but Important)

1. ✅ CQ 160: Score matches ScoreStatsAggregator (if applicable)
2. ✅ All `totaling_method` patterns work correctly
3. ✅ Edge cases handled gracefully
4. ✅ Test script can be run independently

---

## Rollback Plan

If tests reveal regressions:

1. **Immediate:** Revert StandardCalculator changes (git revert)
2. **Investigate:** Review test failures and determine root cause
3. **Fix:** Address issues and re-test
4. **Re-deploy:** Once all tests pass

**Rollback Command:**
```bash
git revert <commit-hash>
```

---

## Future Enhancements

After successful implementation:

1. **Add to CI/CD:** Include in automated regression suite
2. **Expand Coverage:** Add more test cases as new contest patterns emerge
3. **Performance Testing:** Verify no performance regressions
4. **Documentation:** Update StandardCalculator docstring with `applies_to` handling
5. **Architecture Validation:** Add check to ArchitectureValidator to ensure all calculators respect `applies_to`

---

## Related Documents

- `TECHNICAL_DEBT.md` - Technical debt entry (mark as completed after implementation)
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_DISCUSSION.md` - Detailed discussion
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_TESTING_PLAN.md` - Testing plan
- `DevNotes/Decisions_Architecture/PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md` - Architecture principle
- `contest_tools/score_calculators/standard_calculator.py` - File to be updated
- `contest_tools/data_aggregators/score_stats.py` - Reference implementation (lines 176-179)
- `contest_tools/contest_definitions/arrl_dx_cw.json` - Example asymmetric contest definition

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review implementation plan
- [ ] Create test script structure
- [ ] Run baseline tests (confirm bug)
- [ ] Establish golden reference

### Implementation
- [ ] Add location type extraction to StandardCalculator
- [ ] Filter multiplier rules by `applies_to`
- [ ] Update multiplier_columns extraction
- [ ] Change loop to use filtered rules
- [ ] Code review

### Validation
- [ ] Run full test suite
- [ ] Verify all regression tests pass
- [ ] Verify ARRL DX fix works
- [ ] Manual spot-checking
- [ ] Update TECHNICAL_DEBT.md

### Post-Implementation
- [ ] Document any edge cases discovered
- [ ] Update docstrings if needed
- [ ] Consider adding to CI/CD
- [ ] Update architecture validation if applicable

---

**Last Updated:** 2026-01-20  
**Status:** Ready for Implementation  
**Estimated Effort:** 4-6 hours (including testing)
