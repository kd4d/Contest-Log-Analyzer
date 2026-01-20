# StandardCalculator `applies_to` Filtering - Testing Plan

## Date
2026-01-19

## Objective

Update `StandardCalculator` to handle `applies_to` filtering (as discussed in PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md) while ensuring no regressions for existing contests that use the default calculator.

## Change Summary

**What:** Add `applies_to` filtering to `StandardCalculator.calculate()`

**Where:** `contest_tools/score_calculators/standard_calculator.py` (line ~83)

**Why:** 
- ARRL DX (and potentially CQ 160) use `StandardCalculator` but have asymmetric multiplier rules
- Without `applies_to` filtering, multipliers are counted twice (2x scores)
- Core modules should handle declarative rules from contest definitions

**Expected Impact:**
- Fixes double-counting for ARRL DX (W/VE vs DX)
- No impact on symmetric contests (most others)
- Aligns StandardCalculator with ScoreStatsAggregator logic

## Contests Affected

### Contests Using StandardCalculator (Default)
These contests do **NOT** specify a custom `time_series_calculator`, so they use `StandardCalculator`:

1. **ARRL DX CW/SSB** - Has `applies_to` filtering (W/VE vs DX) ⚠️ **PRIMARY TARGET**
2. **ARRL 10** - `totaling_method: once_per_mode`
3. **ARRL SS** - `totaling_method: once_per_log`
4. **ARRL FD** - `totaling_method: once_per_mode`
5. **CQ WW CW/SSB/RTTY** - Standard `sum_by_band` (no `applies_to`)
6. **CQ WPX CW/SSB** - `totaling_method: once_per_log`
7. **CQ 160** - Has `applies_to` filtering (W/VE) ⚠️ **NEEDS TESTING**
8. **IARU HF** - `totaling_method: sum_by_band` (no `applies_to`)

### Contests with Custom Calculators (NOT AFFECTED)
These have their own calculators and won't use `StandardCalculator`:
- **WAE** - `wae_calculator` (has custom logic)
- **NAQP** - `naqp_calculator` (has custom logic)
- **WRTC** - `wrtc_calculator` (has custom logic)

## Testing Strategy

### Principle: Golden Reference Pattern

**Use ScoreStatsAggregator as the "golden reference"** since it already correctly handles `applies_to` filtering and all `totaling_method` variations.

**Test Approach:**
1. Process each contest log through both calculators
2. Compare final scores and intermediate metrics
3. Assert they match (within tolerance for time-series accumulation differences)

### Test Categories

#### 1. Regression Tests (Existing Contests)
Test that adding `applies_to` filtering doesn't break symmetric contests:

**Symmetric Contests (No `applies_to`):**
- ARRL 10 (`once_per_mode`)
- ARRL SS (`once_per_log`)
- ARRL FD (`once_per_mode`)
- CQ WW CW/SSB/RTTY (`sum_by_band`)
- CQ WPX CW/SSB (`once_per_log`)
- IARU HF (`sum_by_band`)

**Expected:** Scores should be identical before and after change (no `applies_to` rules = no filtering happens)

#### 2. Fix Validation Tests (ARRL DX)
Test that the fix works correctly:

**ARRL DX CW/SSB:**
- W/VE operator: Should count DXCC multipliers only (not STPROV)
- DX operator: Should count STPROV multipliers only (not DXCC)
- Final score should match ScoreStatsAggregator

**Expected:** 
- Before change: 2x scores (both rules counted)
- After change: Correct scores (only applicable rule counted)

#### 3. Edge Case Tests
Test boundary conditions:

- Contest with `applies_to` but operator location type not set
- Contest with `applies_to` but location type doesn't match any rule
- Contest with mixed rules (some with `applies_to`, some without)

#### 4. Comprehensive Pattern Tests
Test all `totaling_method` combinations:

- `sum_by_band` with `applies_to`
- `once_per_log` with `applies_to`
- `once_per_mode` with `applies_to`
- `once_per_band_no_mode` with `applies_to` (CQ 160)

## Test Script Design

### Script: `test_code/test_standard_calculator_applies_to.py`

**Purpose:** Automated regression and validation testing

**Test Data Requirements:**
1. Real contest logs (from `CONTEST_LOGS_REPORTS/Logs/` or `regressiontest.bat`)
2. Logs covering all contest patterns listed above
3. Known-good baseline scores (from current ScoreStatsAggregator)

**Test Structure:**

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
        # Test: DX operator log (Alaska, Hawaii, etc.)
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
        # Edge case: Should fall back to processing all rules?
```

### Test Execution Flow

1. **Load Test Logs**
   - Use existing logs from `regressiontest.bat` patterns
   - Load logs with known location types (for ARRL DX testing)

2. **Process Through Both Calculators**
   ```python
   # Reference: ScoreStatsAggregator (golden reference)
   score_agg = ScoreStatsAggregator([log])
   reference_score = score_agg.get_score_breakdown()['logs'][callsign]['final_score']
   reference_mults = score_agg.get_score_breakdown()['logs'][callsign]['total_summary']
   
   # Test: StandardCalculator
   calculator = StandardCalculator()
   calculator_df = calculator.calculate(log, df_non_dupes)
   calculator_score = int(calculator_df['score'].iloc[-1])
   calculator_mults = int(calculator_df['total_mults'].iloc[-1])
   ```

3. **Compare Results**
   ```python
   # Scores should match (time-series may have minor rounding differences)
   assert abs(calculator_score - reference_score) <= tolerance
   
   # Multiplier counts should match exactly
   assert calculator_mults == reference_total_mults
   ```

4. **Report Results**
   - Pass/Fail per contest
   - Detailed differences if failures occur
   - Summary report of all tests

## Test Data Management

### Existing Test Logs

From `regressiontest.bat`, we have logs for:
- CQ WW CW (k3lr, w3lpl, k1lz)
- ARRL SS CW (kd4d, k3mm, aa3b)
- CQ 160 CW (kd4d, n0ni)
- CQ WPX CW (k3lr, kc1xx, ni4w, kb4dx)
- ARRL 10 (ve3ej, vp2vmm)
- ARRL DX CW (k5zd, aa3b, 8p5a, p44w)
- ARRL DX SSB (8p5a, zf1a)
- ARRL FD (w1op, w3ao)
- IARU HF (nn3w, n9nb, gb5wr, gb9wr)

### Additional Test Logs Needed

**For Complete Coverage:**
1. **ARRL DX W/VE operator** - Need 48-state US or Canadian station
   - Suggested: K3LR, W3LPL (if available in DX contests)
   
2. **ARRL DX DX operator** - Need Alaska/Hawaii/US possession/international
   - From list: 8p5a (8P - Barbados), p44w (P4 - Aruba), zf1a (ZF - Cayman Islands)

3. **Verify Location Types** - Need to confirm location type detection works correctly

### Test Log Location

Test logs should be stored in:
- Primary: `CONTEST_LOGS_REPORTS/Logs/` (existing location)
- Reference in test script: Use paths from `regressiontest.bat` as baseline

## Implementation Plan

### Phase 1: Create Test Script (Before Changes)

1. **Create test script structure**
   ```bash
   test_code/test_standard_calculator_applies_to.py
   ```

2. **Implement baseline tests** (using current StandardCalculator)
   - Run all test cases
   - Capture baseline results (will show failures for ARRL DX)
   - Document expected vs actual for ARRL DX (confirms the bug)

3. **Establish golden reference**
   - Use ScoreStatsAggregator as truth
   - Verify all symmetric contests match
   - Document ARRL DX mismatch (2x issue)

### Phase 2: Implement Change

1. **Add `applies_to` filtering to StandardCalculator**
   - Line ~83: Add location type check
   - Skip rules where `applies_to` doesn't match operator location
   - Match ScoreStatsAggregator logic (lines 168-171)

2. **Code Review**
   - Verify logic matches ScoreStatsAggregator
   - Ensure no side effects on other code paths

### Phase 3: Validate Changes

1. **Run full test suite**
   ```bash
   python test_code/test_standard_calculator_applies_to.py
   ```

2. **Verify Results**
   - ✅ All symmetric contests: No change (regression tests pass)
   - ✅ ARRL DX W/VE: Correct scores (DXCC only)
   - ✅ ARRL DX DX: Correct scores (STPROV only)
   - ✅ CQ 160: Correct scores (if applicable)

3. **Manual Verification**
   - Run `regressiontest.bat` to ensure no unexpected regressions
   - Spot-check a few contest reports visually

4. **Document Results**
   - Update test results
   - Document any edge cases discovered
   - Note any tolerance thresholds needed

## Test Script Implementation Details

### Comparison Tolerance

**Scores:** 
- Allow ±1 point difference for rounding in time-series accumulation
- If difference > 1: Investigate (may indicate real bug)

**Multipliers:**
- Must match exactly (no rounding in multiplier counting)
- If difference > 0: Bug (multiplier counting logic mismatch)

### Error Reporting

```python
def compare_calculators(log, tolerance=1):
    """Compare StandardCalculator vs ScoreStatsAggregator."""
    # Process both
    score_agg_result = ScoreStatsAggregator([log]).get_score_breakdown()
    calculator_result = StandardCalculator().calculate(log, df_non_dupes)
    
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
    
    # ... multiplier comparison ...
    
    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'metrics': {
            'calculator_score': calculator_score,
            'reference_score': reference['final_score'],
            'calculator_mults': calculator_mults,
            'reference_mults': reference['total_summary']
        }
    }
```

### Test Execution

```bash
# Run all tests
python test_code/test_standard_calculator_applies_to.py

# Run specific test
python test_code/test_standard_calculator_applies_to.py --test test_arrl_dx_w_ve_operator

# Verbose output
python test_code/test_standard_calculator_applies_to.py --verbose

# Save results
python test_code/test_standard_calculator_applies_to.py --output results.json
```

## Success Criteria

### Must Pass (Blocking)

1. ✅ All symmetric contests: Scores unchanged (regression tests)
2. ✅ ARRL DX W/VE: Score matches ScoreStatsAggregator (within tolerance)
3. ✅ ARRL DX DX: Score matches ScoreStatsAggregator (within tolerance)
4. ✅ No new warnings in regression test output

### Should Pass (Non-Blocking but Important)

1. ✅ CQ 160: Score matches ScoreStatsAggregator (if applicable)
2. ✅ All `totaling_method` patterns work correctly
3. ✅ Edge cases handled gracefully

## Risk Mitigation

### Risk 1: Breaking Symmetric Contests

**Mitigation:**
- `applies_to` filtering only activates when rule has `applies_to` field
- Symmetric contests have no `applies_to` → no filtering happens
- Test all symmetric contests in regression suite

### Risk 2: Location Type Not Set

**Mitigation:**
- Check if `log_location_type` is None or empty
- If no location type: Process all rules (backward compatible)
- Add test case for this scenario

### Risk 3: Time-Series Accumulation Differences

**Mitigation:**
- Use ScoreStatsAggregator as reference (calculates from final totals)
- StandardCalculator uses time-series (may have minor rounding)
- Allow ±1 point tolerance for legitimate differences

## Rollback Plan

If tests reveal regressions:

1. **Immediate:** Revert StandardCalculator changes
2. **Investigate:** Review test failures and determine root cause
3. **Fix:** Address issues and re-test
4. **Re-deploy:** Once all tests pass

## Future Enhancements

After successful implementation:

1. **Add to CI/CD:** Include in automated regression suite
2. **Expand Coverage:** Add more test cases as new contest patterns emerge
3. **Performance Testing:** Verify no performance regressions
4. **Documentation:** Update StandardCalculator docstring with `applies_to` handling

## Related Documents

- [PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md](./PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md) - Architecture decision
- [SCORING_ARCHITECTURE_ANALYSIS.md](../Discussions/SCORING_ARCHITECTURE_ANALYSIS.md) - Scoring paths analysis
- `regressiontest.bat` - Existing regression test patterns
- `run_regression_test.py` - Regression test framework
