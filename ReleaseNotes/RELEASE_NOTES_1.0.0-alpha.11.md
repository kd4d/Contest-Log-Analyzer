# Release Notes: v1.0.0-alpha.11

**Release Date:** January 24, 2026  
**Tag:** `v1.0.0-alpha.11`

**Note:** These release notes include all changes from the feature branch `feature/1.0.0-alpha.11` merged to master, plus any commits made directly to master since `v1.0.0-alpha.10`.

---

## Summary

This release adds multiplier timeline reports, implements Sweepstakes contest-wide QSO breakdown visualization, enhances report suppression for single-mode contests, improves diagnostic logging, fixes CQ 160 multiplier detection, and includes comprehensive documentation updates.

---

## Added

### Multiplier Timeline Reports
- **Added multiplier timeline reports for single-log and multi-log analysis**
  - `text_multiplier_timeline.py` - Shows hourly progression of unique multipliers for single log
  - `text_multiplier_timeline_comparison.py` - Shows multiplier acquisition timeline for multi-log comparison
  - Follows rate sheet report structure pattern
  - Included in bulk download, excluded from dashboards (per design decision)

### Sweepstakes Contest-Wide QSO Breakdown Visualization
- **Implemented Phase 1 contest-wide QSO breakdown for Sweepstakes**
  - Primary view: Contest-wide QSO breakdown (not band-by-band)
  - Secondary view: QSO Band Distribution (informational only)
  - Fixes misleading band-by-band visualization for contests with contest-wide QSO counting
  - Uses direct Plotly embedding for responsive charts
  - Dashboard integration with conditional tab rendering

### Report Suppression Enhancements
- **Added smart suppression to rate sheet detail sections**
  - Suppresses detail sections for single-mode contests
  - Reduces clutter in reports when detail sections would be redundant
  - Applies to rate sheet reports automatically

### Diagnostic Logging Improvements
- **Elevated diagnostic messages to WARNING level**
  - Diagnostic messages now use `[DIAG]` prefix and WARNING/ERROR level
  - Ensures diagnostics are visible at default log level settings
  - Added diagnostic log analysis documentation

### Documentation Updates
- **Implemented comprehensive documentation versioning policy**
  - Category-based versioning system (A, B, C, D)
  - Clear rules for when to update documentation versions
  - Updated Sweepstakes implementation status
  - Enhanced PowerShell syntax warnings in AI Agent Rules
  - Updated regression testing baseline directory structure documentation

### Multiplier Breakdown Report Enhancements
- **Added mode dimension support to text and HTML multiplier breakdown reports**
  - Supports single-band, multi-mode contests (e.g., ARRL 10 Meter)
  - Shows multiplier breakdowns by mode when applicable
  - Removed Common and Missed columns from single-log reports (not applicable)

---

## Fixed

### CQ 160 Multiplier Detection
- **Fixed IG9/IH9 handling and applies_to filter**
  - Correctly detects multipliers for CQ 160 contest
  - Properly applies multiplier filtering rules

### Parser Improvements
- **Skip unmatched QSOs and add warning counters**
  - Parser now skips QSOs that don't match expected format
  - Adds warning counters for tracking parsing issues
  - Improves error handling and reporting

### Diagnostic System
- **Filter entries by report_id in finalize_report**
  - Ensures diagnostic entries are properly associated with reports
  - Prevents cross-report contamination of diagnostic data

### Sweepstakes Dashboard
- **Fixed ARRL SS CW multiplier dashboard reference line alignment**
  - Reference line now properly aligned with grid system
  - Refactored to use grid-lines-container coordinate system

### QSO Chart Improvements
- **Fixed QSO chart legend positioning**
  - Improved legend placement for better readability
  - Migrated band distribution to direct Plotly embedding
  - Better responsive behavior

### WRTC Scoring
- **Fixed WRTC scoring calculation and UI improvements**
  - Corrected scoring calculation for WRTC contests
  - Improved UI for WRTC contest selection
  - Specified WRTC supported years (2018, 2022, 2026) in Welcome popup

### Sweepstakes Reports
- **Suppressed misleading QSO reports and added clarifications**
  - Suppresses band-by-band QSO breakdown for Sweepstakes (misleading for contest-wide counting)
  - Added clarifications about contest-wide QSO counting
  - Enhanced Sweepstakes multiplier dashboard

### Error Handling
- **Resolved pandas FutureWarnings and improved error messages**
  - Fixed deprecated pandas API usage
  - Improved error messages for better debugging

### Docker Build
- **Added .dockerignore to reduce image size**
  - Excludes unnecessary files from Docker build context
  - Reduces build time and image size

---

## Changed

### Callsign Naming Protocol
- **Standardized callsign naming protocol across all file and directory names**
  - Consistent naming convention for callsigns in filenames
  - Portable designators (e.g., `/` → `-`)
  - Improved cross-platform compatibility

### Supported Contests Documentation
- **Enhanced Sweepstakes multiplier dashboard and updated supported contests documentation**
  - Updated documentation to reflect all supported contests
  - Added ARRL 10 Meter to supported contests lists
  - Clarified contest support levels (Full Dashboard vs ZIP-only)

### Git Configuration
- **Added comprehensive Python cache ignore patterns**
  - Updated .gitignore to ignore __pycache__ directories recursively
  - Added .cursor/ to .gitignore to exclude Cursor IDE debug files
  - Improved repository cleanliness

---

## Technical Details

### Files Changed
- `contest_tools/reports/text_multiplier_timeline.py` - New multiplier timeline report
- `contest_tools/reports/text_multiplier_timeline_comparison.py` - New comparison timeline report
- `contest_tools/reports/chart_qso_breakdown_contest_wide.py` - Contest-wide QSO breakdown
- `contest_tools/reports/qso_chart_helpers.py` - Helper functions for QSO charts
- `contest_tools/data_aggregators/categorical_stats.py` - Band distribution breakdown
- `contest_tools/reports/text_rate_sheet.py` - Smart suppression for single-mode contests
- `contest_tools/reports/text_multiplier_breakdown.py` - Mode dimension support
- `contest_tools/reports/html_multiplier_breakdown.py` - Mode dimension support
- `web_app/analyzer/views.py` - Dashboard integration, diagnostic improvements
- `web_app/analyzer/templates/analyzer/home.html` - WRTC years in popup, ARRL 10 Meter support
- `web_app/analyzer/templates/analyzer/about.html` - Updated supported contests
- `README.md` - Added ARRL 10 Meter to supported contests
- `Docs/AI_AGENT_RULES.md` - Enhanced PowerShell syntax warnings, workflow updates
- `Docs/VersionManagement.md` - Comprehensive versioning policy
- `.gitignore` - Python cache patterns, Cursor IDE files
- `.dockerignore` - Docker build optimization

### Commits Included
- Add multiplier timeline reports (single-log and multi-log)
- Implement Sweepstakes contest-wide QSO breakdown visualization
- Add smart suppression to rate sheet detail sections
- Elevate diagnostic messages to WARNING level
- Fix CQ 160 multiplier detection
- Add mode dimension support to multiplier breakdown reports
- Standardize callsign naming protocol
- Fix WRTC scoring calculation and UI
- Resolve pandas FutureWarnings
- Add comprehensive documentation versioning policy
- Update supported contests documentation
- Improve gitignore and dockerignore patterns

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a feature and enhancement release with no breaking changes.

Existing sessions and reports continue to work as before. New features (multiplier timeline reports, contest-wide QSO breakdown) are automatically available for supported contests.

---

## Documentation

- Implemented comprehensive documentation versioning policy
- Updated Sweepstakes implementation status
- Enhanced PowerShell syntax warnings in AI Agent Rules
- Updated regression testing baseline directory structure documentation
- Updated supported contests documentation (added ARRL 10 Meter)
- Enhanced release workflow documentation (two-commit process clarification)

---
