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

---

### Once Per Mode Multiplier Calculation Fixes

**Status:** ✅ Completed (2026-01-19)

**Problems Fixed:**

1. **Multiplier Dashboard "All Multipliers" Tab Redundancy:**
   - **Issue:** "All Multipliers" tab shown even when contest defines only one multiplier type (e.g., ARRL DX for US/VE entries)
   - **Fix:** Hide "All Multipliers" tab when `multiplier_count == 1` (based on contest definition, not log data)
   - **Decision Logic:** Filters `multiplier_rules` by `applies_to` (location_type) for asymmetric contests like ARRL DX
   - **Example:** ARRL DX for W/VE entries only has "DXCC Countries" multiplier type, so tab is hidden

2. **Score Summary 'ALL' Line Incorrect Calculation:**
   - **Issue:** For `once_per_mode` contests (ARRL 10), 'ALL' line showed union of multipliers across modes instead of sum
   - **Example:** ARRL 10 showed 51 US States in 'ALL' (union) instead of 102 (51+51 sum)
   - **Fix:** For `once_per_mode`, calculate 'ALL' row by summing multipliers from individual mode rows
   - **Result:** 'ALL' line now matches TOTAL line (e.g., 102 US States, 22 Provinces, 12 Mexican States, 192 DXCC)

3. **Breakdown Report Totals Incorrect for Once Per Mode:**
   - **Issue:** Totals row summed "new multipliers per hour" instead of cumulative unique multipliers per mode
   - **Fix:** For `once_per_mode`, use cumulative unique multipliers per mode from score summary calculation
   - **Result:** Breakdown totals now match score summary (e.g., CW: 174, PH: 154, Total: 328)

4. **Cumulative Multiplier Tracking Mismatch:**
   - **Issue:** CUMM column showed 315 instead of 328 for ARRL 10
   - **Root Cause:** TimeSeriesAggregator tracked multipliers in single set per mode instead of per rule per mode
   - **Fix:** Track multipliers per rule (column) per mode, then sum (matches score summary logic)
   - **Result:** CUMM column now matches score summary TOTAL (328 = 174+154)

**Files Modified:**
1. **`web_app/analyzer/views.py`**:
   - Added `multiplier_count` to context (count of applicable multiplier rules from contest definition)
   - Filters `multiplier_rules` by `applies_to` (location_type) for asymmetric contests
   - Falls back to log data count if contest definition unavailable

2. **`web_app/analyzer/templates/analyzer/multiplier_dashboard.html`**:
   - Conditionally render "All Multipliers" tab only when `multiplier_count > 1`
   - Make single multiplier tab active by default when only one type exists

3. **`contest_tools/data_aggregators/score_stats.py`**:
   - Fixed `_calculate_log_score()` to sum multipliers from mode rows for 'ALL' line when `once_per_mode`
   - Checks for `once_per_mode` totaling method before creating 'ALL' row

4. **`contest_tools/reports/text_breakdown_report.py`**:
   - Fixed totals calculation to use cumulative unique multipliers per mode for `once_per_mode`
   - Uses ScoreStatsAggregator calculation to get accurate per-mode totals

5. **`contest_tools/data_aggregators/time_series.py`**:
   - Changed multiplier tracking structure from `{mode: set()}` to `{mode: {col: set()}}` for `once_per_mode`
   - Tracks multipliers per rule (column) per mode, then sums (matches score summary logic)
   - Fixed cumulative calculation to sum unique multipliers per rule per mode

**Resolution:**
- All identified issues have been fixed
- Score Summary 'ALL' line now matches TOTAL for `once_per_mode` contests
- Breakdown Report totals match Score Summary totals
- CUMM column matches Score Summary TOTAL
- Multiplier Dashboard hides redundant "All Multipliers" tab appropriately

**Technical Notes:**
- Fixes ensure `once_per_mode` contests (ARRL 10, etc.) calculate multipliers correctly per contest rules
- Multipliers count once per mode, then sum across modes (not union)
- All calculations respect contest definition `totaling_method` from JSON
- Decision logic for "All Multipliers" tab based on contest definition, not log data (handles asymmetric contests correctly)

**Affected Contests:**
- **ARRL 10 Meter:** All fixes apply (uses `once_per_mode` for all multiplier rules)
- **Other `once_per_mode` contests:** All fixes apply if they use this totaling method

**Related Commit:** `cc4426427cf740902a83c8b0982b8e4d3e361d4b`