# Release Notes: v1.0.0-alpha.14

**Release Date:** January 26, 2026  
**Tag:** `v1.0.0-alpha.14`

**Note:** These release notes include all changes from the feature branch `feature/1.0.0-alpha.14` merged to master, plus any commits made directly to master since `v1.0.0-alpha.13`.

---

## Summary

This release fixes critical dashboard issues for single-log analysis. The main highlights include fixing blank multiplier breakdown reports (Countries/Zones) and resolving the Rate Detail tab 404 error for single logs. Both issues were related to filename format handling for single-log reports.

---

## Fixed

### Dashboard Fixes for Single-Log Analysis
- **Fixed Rate Detail tab on QSO Dashboard for single logs**
  - Resolved 404 error when accessing Rate Detail tab for single logs
  - Issue was caused by incorrect URL construction using old filename format
  - Now dynamically discovers correct rate sheet report paths from manifest
  - Supports both new (`rate_sheet--{callsign}.txt`) and old (`rate_sheet_{callsign}.txt`) filename formats
  - **Impact:** Rate Detail tab now works correctly for single-log analyses

- **Fixed multiplier breakdown reports (Countries/Zones) for single logs**
  - Resolved blank reports appearing in Multiplier Dashboard Analysis Reports tab
  - Issue was caused by Bootstrap tab button not having `active` class when tab pane was active
  - JavaScript was unable to identify the initially active tab for single-log cases
  - Synchronized `active` class state between tab button and tab pane
  - **Impact:** Multiplier breakdown reports now display correctly for single-log analyses

---

## Technical Details

### Files Changed
- `web_app/analyzer/views.py` - Added dynamic rate sheet URL discovery, fixed multiplier dashboard tab activation
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` - Updated to use dynamically discovered rate sheet URLs
- `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` - Fixed tab button active state for single-log cases

### Commits Included
- fix(dashboard): fix single-log multiplier breakdown reports and rate detail tab
- Remove diagnostic messages for single log filenames in the QSO and Multiplier dashboards.
- Commit Alpha.13 release notice and VPS update instructions for future reference.

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a bug fix release with no breaking changes.

Existing sessions and reports continue to work as before. All fixes are automatically applied to new analyses.

---

## Documentation

- Updated version references across all documentation files to match project release v1.0.0-alpha.14

---
