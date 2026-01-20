# Release Notes: v1.0.0-alpha.10

**Release Date:** January 20, 2026  
**Tag:** `v1.0.0-alpha.10`

---

## Summary

This release fixes critical multiplier calculation bugs for `once_per_mode` contests (like ARRL 10 Meter), adds ARRL DX contest support, improves dashboard UI with abbreviated multiplier names to reduce compression, and reorganizes development documentation structure.

---

## Fixed

### Once Per Mode Multiplier Calculation Fixes
- **Fixed Score Summary 'ALL' line incorrect calculation for `once_per_mode` contests**
  - Root cause: 'ALL' line showed union of multipliers across modes instead of sum
  - Example: ARRL 10 showed 51 US States in 'ALL' (union) instead of 102 (51+51 sum)
  - Solution: For `once_per_mode`, calculate 'ALL' row by summing multipliers from individual mode rows
  - Impact: 'ALL' line now matches TOTAL line (e.g., 102 US States, 22 Provinces, 12 Mexican States, 192 DXCC)

- **Fixed Breakdown Report totals incorrect for once per mode contests**
  - Root cause: Totals row summed "new multipliers per hour" instead of cumulative unique multipliers per mode
  - Solution: For `once_per_mode`, use cumulative unique multipliers per mode from score summary calculation
  - Impact: Breakdown totals now match score summary (e.g., CW: 174, PH: 154, Total: 328)

- **Fixed Cumulative Multiplier Tracking Mismatch**
  - Root cause: CUMM column showed 315 instead of 328 for ARRL 10
  - Solution: TimeSeriesAggregator now tracks multipliers per rule (column) per mode, then sums (matches score summary logic)
  - Impact: CUMM column now matches score summary TOTAL (328 = 174+154)

- **Fixed Multiplier Dashboard "All Multipliers" tab redundancy**
  - Issue: "All Multipliers" tab shown even when contest defines only one multiplier type (e.g., ARRL DX for US/VE entries)
  - Solution: Hide "All Multipliers" tab when `multiplier_count == 1` (based on contest definition, not log data)
  - Impact: Cleaner UI for contests with single multiplier types

### Dashboard UI Improvements
- **Fixed compressed multiplier name tabs in dashboard tables**
  - Abbreviated multiplier names in scoreboard table headers and multiplier dashboard tabs
  - Abbreviations: Provinces → Provs, Mexican States → Mex, ITU Regions → Regs
  - Handles prefixed versions (e.g., US Provinces → US Provs, Mexican Regions → Mex Regs)
  - Impact: Reduces space compression in ARRL Analysis Results Dashboard tabs and table columns

---

## Added

### ARRL DX Contest Support
- **Added full ARRL DX contest support**
  - Supports asymmetric contest rules (different multipliers for W/VE vs DX entries)
  - Multiplier rules filtered by `applies_to` (location_type) based on entry class
  - Handles Canadian Provinces and DXCC Countries multipliers correctly
  - Includes public log fetching and preflight validation

### Documentation
- **Reorganized DevNotes directory structure**
  - New directory structure: `DevNotes/Archive/`, `DevNotes/Decisions_Architecture/`, `DevNotes/Discussions/`
  - Added `DevNotes/README.md` with organization guidelines
  - Moved historical planning documents to Archive
  - Organized architecture decisions and discussion documents

- **Added critical git workflow documentation**
  - Added stash-before-clean rule to prevent data loss
  - Documented StandardCalculator `applies_to` testing plan
  - Updated HANDOVER.md with once per mode multiplier fixes summary
  - Documented refined plugin architecture boundary decision

---

## Changed

### Score Statistics Aggregator
- **Enhanced once per mode multiplier calculation**
  - Fixed `_calculate_log_score()` to sum multipliers from mode rows for 'ALL' line when `once_per_mode`
  - Checks for `once_per_mode` totaling method before creating 'ALL' row
  - Ensures accurate multiplier totals for contests using per-mode totaling

### Breakdown Report Generator
- **Improved totals calculation for once per mode contests**
  - Uses cumulative unique multipliers per mode for `once_per_mode` contests
  - Uses ScoreStatsAggregator calculation to get accurate per-mode totals
  - Breakdown totals now match score summary totals

### Time Series Aggregator
- **Enhanced multiplier tracking for once per mode contests**
  - Changed multiplier tracking structure from `{mode: set()}` to `{mode: {col: set()}}` for `once_per_mode`
  - Tracks multipliers per rule (column) per mode, then sums (matches score summary logic)
  - Fixed cumulative calculation to sum unique multipliers per rule per mode

### Multiplier Dashboard
- **Improved multiplier tab display logic**
  - Conditionally renders "All Multipliers" tab only when `multiplier_count > 1`
  - Makes single multiplier tab active by default when only one type exists
  - Filters `multiplier_rules` by `applies_to` (location_type) for asymmetric contests

### Template Filters
- **Added `abbreviate_multiplier` template filter**
  - Abbreviates multiplier names for compact tab and table header display
  - Handles both full names and prefixed versions
  - Reduces space compression in dashboard UI

---

## Technical Details

### Files Changed
- `contest_tools/data_aggregators/score_stats.py` - Fixed once per mode 'ALL' row calculation
- `contest_tools/data_aggregators/time_series.py` - Fixed once per mode multiplier tracking per rule per mode
- `contest_tools/reports/text_breakdown_report.py` - Fixed totals calculation for once per mode
- `web_app/analyzer/views.py` - Added multiplier_count to context, ARRL DX support
- `web_app/analyzer/templates/analyzer/dashboard.html` - Applied abbreviation filter to table headers
- `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` - Conditional "All Multipliers" tab, abbreviated tab labels
- `web_app/analyzer/templatetags/analyzer_extras.py` - Added abbreviate_multiplier filter
- `HANDOVER.md` - Updated with once per mode fixes summary
- DevNotes directory structure reorganized

### Commits Included
- Fix multiplier calculation and UI for once_per_mode contests (ARRL 10, etc.)
- Abbreviate multiplier names in dashboard tables and tabs
- Add ARRL DX contest support and multiplier breakdown fixes
- Fix breakdown report CUMM column and suppress diagnostic messages
- Reorganize DevNotes directory structure
- Add comprehensive documentation for plugin architecture and testing plans

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a bug fix and enhancement release with no breaking changes.

Existing sessions and reports continue to work as before. The fixes improve accuracy of multiplier reporting for `once_per_mode` contests and enhance the dashboard UI with better space utilization.

---

## Documentation

- Reorganized `DevNotes/` directory structure for better organization
- Added `DevNotes/README.md` with organization guidelines
- Updated `HANDOVER.md` with once per mode multiplier fixes summary
- Added StandardCalculator `applies_to` testing plan
- Documented refined plugin architecture boundary decision

---
