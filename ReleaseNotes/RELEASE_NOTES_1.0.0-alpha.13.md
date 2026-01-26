# Release Notes: v1.0.0-alpha.13

**Release Date:** January 26, 2026  
**Tag:** `v1.0.0-alpha.13`

**Note:** These release notes include all changes from the feature branch `feature/1.0.0-alpha.13` merged to master, plus any commits made directly to master since `v1.0.0-alpha.12`.

---

## Summary

This release focuses on UI improvements and report layout fixes. The main highlights include enhanced visibility of tab labels, improved report rendering without iframes, better layout handling for analysis reports, and various bug fixes for report formatting and display issues.

---

## Fixed

### UI Visibility Improvements
- **Enhanced tab label visibility on home page**
  - Increased tab label font size to 1.75rem and made them bold (font-weight: 700)
  - Changed "Public Log Archive" tab text to "Upload from Public Log Archive" for clarity
  - Darkened checkbox borders for "Apply WRTC Scoring Rules" checkboxes (both manual upload and archive sections)
  - **Impact:** Tab labels are now much more prominent and easier to read

### Report Layout and Display Issues
- **Fixed Analysis Reports tab layout and card resizing issues**
  - Improved card layout and resizing behavior in Analysis Reports tab
  - Better handling of content overflow and card dimensions

- **Removed unnecessary horizontal scrollbars from report cards**
  - Fixed horizontal scrollbar issues in report cards
  - Improved content width handling

- **Expanded tab-pane to full width to eliminate unnecessary scrollbars**
  - Tab panes now use full available width
  - Eliminates unnecessary scrollbars in report displays

- **Fixed QSO breakdown report alignment**
  - Aligned '/' symbols vertically in all columns of QSO breakdown report
  - Improved visual consistency in report formatting

### Report Rendering
- **Replaced iframes with direct text rendering in Multiplier Dashboard Analysis Reports**
  - Removed iframe usage in Multiplier Dashboard Analysis Reports
  - Now uses direct text rendering for better performance and compatibility
  - Improved report loading and display

---

## Added

### Report Features
- **Added InactiveTime column to breakdown report**
  - New column showing inactive time in breakdown reports
  - Provides additional timing information for analysis

### Zone Normalization
- **Added zone normalization and fixed CQ 160 mode display**
  - Improved zone handling and normalization
  - Fixed CQ 160 mode display issues

---

## Changed

### Report Formatting
- **Standardized report filename format and improved error handling**
  - Consistent filename format across all reports
  - Enhanced error handling for report generation

### Documentation
- **Added year-over-year comparison feature to future work documentation**
  - Documented planned year-over-year comparison feature
  - Added to future work tracking

---

## Technical Details

### Files Changed
- `web_app/analyzer/templates/analyzer/home.html` - UI visibility improvements, tab label enhancements, checkbox border fixes
- `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` - Replaced iframes with direct text rendering
- Report generation modules - Layout fixes, alignment improvements, filename standardization
- Documentation files - Future work updates

### Commits Included
- Improve UI visibility: enlarge and bold tab labels, update archive tab text, darken checkbox borders
- Fix Analysis Reports tab layout and card resizing issues
- Fix: Remove unnecessary horizontal scrollbars from report cards
- Fix: Expand tab-pane to full width to eliminate unnecessary scrollbars
- feat: Replace iframes with direct text rendering in Multiplier Dashboard Analysis Reports
- feat: Add zone normalization and fix CQ 160 mode display
- refactor: standardize report filename format and improve error handling
- Fix QSO breakdown report: align '/' symbols vertically in all columns
- docs: add year-over-year comparison feature to future work
- feat: add InactiveTime column to breakdown report

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a UI improvement and bug fix release with no breaking changes.

Existing sessions and reports continue to work as before. All improvements are automatically applied to new analyses.

---

## Documentation

- Updated future work documentation with year-over-year comparison feature
- Improved report formatting and error handling documentation

---
