# Release Notes: v1.0.0-alpha.9

**Release Date:** January 18, 2026  
**Tag:** `v1.0.0-alpha.9`

---

## Summary

This release fixes critical multiplier filtering bugs in breakdown reports for contests with mutually exclusive multipliers (like ARRL 10 Meter), separates multiplier tracking for band vs mode dimensions, and adds comprehensive documentation for the mutually exclusive multiplier filtering pattern.

---

## Fixed

### ARRL 10 Meter Multiplier Filtering Bug
- **Fixed breakdown reports showing zero multipliers for ARRL 10 Meter Contest**
  - Root cause: Filtering logic required ALL multiplier columns to be valid, but ARRL 10 uses mutually exclusive multipliers (each QSO has only ONE multiplier column populated)
  - Solution: Changed filtering logic from AND to OR condition - keep rows where ANY multiplier column has a valid value
  - Impact: Breakdown reports now correctly show multipliers for contests with mutually exclusive multiplier types

### Multiplier Tracking Separation
- **Separated multiplier tracking for band vs mode dimensions**
  - Fixed issue where multiplier counting was incorrectly mixing band and mode dimensions
  - Ensures accurate multiplier breakdowns for contests with different dimension requirements
  - Improved multiplier statistics accuracy in breakdown reports

### Missing Logger
- **Added missing logger to time series aggregator**
  - Added proper logging for multiplier calculation warnings
  - Improves debugging capabilities for multiplier-related issues

---

## Changed

### Time Series Aggregator
- **Enhanced multiplier filtering logic for mutually exclusive multipliers**
  - Updated `_calculate_hourly_multipliers` to use OR logic instead of AND logic
  - Handles contests where each QSO has only one multiplier type populated
  - Maintains backward compatibility with contests using multiple multiplier types per QSO

---

## Added

### Documentation
- **Added comprehensive documentation for mutually exclusive multiplier filtering pattern**
  - New file: `DevNotes/MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md`
  - Documents the bug pattern and correct fix pattern for future reference
  - Includes code examples and explanation of when to use this pattern
  - Helps prevent similar bugs in future development

---

## Technical Details

### Files Changed
- `contest_tools/data_aggregators/time_series.py` - Fixed mutually exclusive multiplier filtering, separated band vs mode tracking, added logger
- `DevNotes/MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md` - Documentation of the bug pattern and fix

### Commits Included
- `docs: add mutually exclusive multiplier filtering pattern documentation`
- `fix(breakdown): fix ARRL 10 multiplier filtering and add missing logger`
- `fix(breakdown): separate multiplier tracking for band vs mode dimensions`

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a bug fix release with no breaking changes.

Existing sessions and reports continue to work as before. The fixes improve accuracy of multiplier reporting for contests with mutually exclusive multipliers.

---

## Documentation

- Added `DevNotes/MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md` - Comprehensive documentation of mutually exclusive multiplier filtering bug pattern and fix

---
