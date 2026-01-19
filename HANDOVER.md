# Workflow State Handover

## Current State
- **Status:** Merged feature branch to master
- **Branch:** master
- **Last Commit:** 38fb9b5 (chore: merge CQ WW dashboard feature branch and git workflow tooling)
- **Working Tree:** Clean
- **Version:** 0.160.0-beta.1 (in contest_tools/version.py)

## Next Steps
1. **Test** merged code on master
2. **Patch** bugs as needed (commit fixes to master)
3. **Tag pre-release beta** (e.g., v0.160.0-beta.2) - last tag with old versioning system
4. **Clean up version headers** - Remove Author/Date/Version lines from ~206 files
5. **Tag first "real" beta** - Start fresh with new versioning system (e.g., v1.0.0-beta.1)

## Context/Notes

### Version Cleanup Details
- **Files with version headers:** ~206 files have `# Version: X.X.X-Beta` lines
- **Files with Author lines:** Many files have `# Author: ...` lines
- **Files with Date lines:** Some files have `# Date: ...` lines
- **Standard header format:** See `Docs/Contributing.md` Section 2 (no Author/Date/Version)
- **Risk level:** LOW-MEDIUM (comment lines only, but careful regex needed)

### Git Identity
- **Name:** Mark Bailey (correctly configured)
- **Email:** markkd4d@gmail.com (correctly configured)
- **Latest commit shows:** Mark Bailey <markkd4d@gmail.com> ✓

### Version Management
- **Current version.py:** 0.160.0-beta.1
- **New versioning system:** Git tags as source of truth, version.py for runtime
- **Pre-commit hooks:** Automatically update git hash in version.py
- **Documentation:** See `Docs/Contributing.md` and `Docs/AI_AGENT_RULES.md`

### Workflow Notes
- **Merged branch:** cqww_dashboard_oneortwologs (26 commits)
- **Merge strategy:** --no-ff (preserves branch history)
- **Next phase:** Testing and patching (manual work)
- **After testing:** Version cleanup (automated task for agent)
- **After cleanup:** Tag first beta with new versioning system

### Multiplier Breakdown Report Fix

**Status:** ✅ Completed (2026-01-19)

**Problem:** Breakdown report multiplier totals did not match scoreboard totals. For example, K1LZ showed 140 multipliers in CUMM column vs 625 in scoreboard for ARRL DX CW.

**Root Causes Identified and Fixed:**
1. **Data Source Inconsistency:** `MultiplierStatsAggregator` and `TimeSeriesAggregator` used `get_processed_data()` (includes dupes) while `ScoreStatsAggregator` used `get_valid_dataframe(log, include_dupes=False)` - **FIXED**
2. **Incorrect Multiplier Tracking:** `TimeSeriesAggregator._calculate_hourly_multipliers()` used global multiplier tracking for all contests, breaking `sum_by_band` contests like ARRL DX - **FIXED**
3. **Missing Filters:** Breakdown calculations didn't filter zero-point QSOs or filter multiplier rules by location type for ARRL DX - **FIXED**
4. **CUMM Column Calculation:** Cumulative multiplier totals not correctly calculated based on `totaling_method` - **FIXED**

**Files Modified:**
1. **`contest_tools/data_aggregators/multiplier_stats.py`**:
   - Changed `get_multiplier_breakdown_data()` to use `get_valid_dataframe(log, include_dupes=False)` instead of `get_processed_data()`
   - Added zero-point QSO filtering when `mults_from_zero_point_qsos` is false
   - Added location type filtering for ARRL DX (only counts applicable multiplier rules)

2. **`contest_tools/data_aggregators/time_series.py`**:
   - Changed `get_time_series_data()` to use `get_valid_dataframe(log, include_dupes=False)` instead of `get_processed_data()`
   - Added zero-point QSO filtering when `mults_from_zero_point_qsos` is false
   - Fixed `_calculate_hourly_multipliers()` to respect `totaling_method` from multiplier rules:
     - `once_per_log` (ARRL SS, WPX): Uses global tracking - multiplier counts once across all bands
     - `sum_by_band` (ARRL DX): Uses per-band tracking - same multiplier can count on different bands
     - `once_per_band_no_mode`: Uses per-band tracking
     - Default: Per-band tracking for other methods
   - Added location type filtering for ARRL DX
   - Fixed cumulative multiplier calculation to match band-by-band totals for `sum_by_band` contests

3. **`contest_tools/reports/text_breakdown_report.py`**:
   - Fixed CUMM column totals row to correctly display final cumulative multipliers
   - Fixed totals row to include Total, CUMM, and Score columns

**Resolution:**
- All identified issues have been fixed
- Breakdown report totals now match scoreboard totals
- CUMM column correctly displays cumulative multipliers matching band-by-band totals
- Diagnostic messages removed (no longer needed - issue resolved)

**Technical Notes:**
- The fix ensures both breakdown and scoreboard use the same data source (`get_valid_dataframe`)
- The fix respects contest-specific `totaling_method` from JSON definitions
- For ARRL DX, only applicable multiplier rules are counted (DXCC for W/VE, STPROV for DX)
- Zero-point QSOs are excluded from multiplier counts for contests where `mults_from_zero_point_qsos` is false

---

### StandardCalculator `applies_to` Field Support Issue (Deferred)

**Status:** 🔍 Identified, ⏸️ Deferred (2026-01-19)

**Problem:** `StandardCalculator` (default time-series score calculator) does not respect the `applies_to` field in multiplier rules, causing incorrect score calculations for asymmetric contests like ARRL DX.

**Symptom:**
- ARRL DX: Plugin calculator shows correct score (e.g., 30,843,750)
- ScoreStatsAggregator calculated score shows exactly half (e.g., 15,421,875)
- Score difference is exactly 2x, indicating multiplier double-counting

**Root Cause:**
- ARRL DX has asymmetric multiplier rules (DXCC for W/VE, STPROV for DX)
- `StandardCalculator` counts ALL multiplier rules without filtering by `applies_to`
- For W/VE operators, it counts both DXCC (correct) and STPROV (incorrect), causing 2x multiplier count
- ARRL DX uses `StandardCalculator` because it lacks a `time_series_calculator` definition (only has `scoring_module`)

**Current Workaround:**
- `ScoreStatsAggregator` uses the plugin calculator's score as authoritative (dashboard shows correct score)
- However, time-series score calculations (used in animations) still show incorrect values

**Proposed Solution:**
- Add `applies_to` filtering to `StandardCalculator` (similar to other aggregators)
- Filter multiplier rules based on `log_location_type` before processing
- Only process multiplier rules where `applies_to` is None or matches `log_location_type`

**Risk Assessment:**
- **Risk Level:** MEDIUM (potentially breaking change)
- **Affected Contests:** All contests using `StandardCalculator` (ARRL 10, ARRL SS, ARRL FD, CQ WW, CQ WPX, IARU HF, CQ 160, ARRL DX)
- **Mitigation:** Comprehensive regression testing required before implementation

**Decision:**
- **Status:** Deferred until comprehensive regression testing can be performed
- **Reason:** High risk of breaking changes requires extensive test coverage
- **Testing Plan:** See `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_TESTING_PLAN.md`

**Related Documentation:**
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_DISCUSSION.md` - Detailed discussion
- `TECHNICAL_DEBT.md` - Technical debt entry
- `DevNotes/Decisions_Architecture/PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md` - Architecture principle