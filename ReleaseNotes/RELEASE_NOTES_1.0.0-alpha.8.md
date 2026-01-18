# Release Notes: v1.0.0-alpha.8

**Release Date:** January 18, 2026  
**Tag:** `v1.0.0-alpha.8`

---

## Summary

This release adds CTY file inclusion in download bundles, CQ 160 Meter Contest support, custom CTY file upload capabilities, and dashboard score report enhancements.

---

## Added

### CTY File Inclusion in Download Bundle
- **CTY file now included in download bundle** at reports root directory
  - CTY file is automatically added to the download bundle at `reports/YYYY/contest/event/calls/cty_file.dat`
  - Works for both custom uploaded CTY files and default system CTY files
  - Provides complete context for report analysis without requiring separate CTY file lookup

### CQ 160 Meter Contest Support
- **Full support for CQ 160 Meter Contest** (CW and SSB variants)
  - Contest parser recognizes both `CQ-160-CW` and `CQ-160-SSB` variants
  - Exchange parsing rules for both CW and SSB formats
  - Multiplier resolver supports STPROV and DXCC multipliers
  - Dashboard integration with score reports

### Custom CTY File Upload
- **Enhanced custom CTY file upload support**
  - Users can upload custom CTY files for analysis
  - Clear "CUSTOM CTY FILE" indicator in reports and metadata
  - Uploaded files are included in download bundle
  - Maintains backward compatibility with default CTY selection

---

## Changed

### Dashboard Score Reports
- **Enhanced dashboard score reporting**
  - Eliminated cache dependency for contest definitions
  - Improved score calculation accuracy
  - Better handling of contest-specific scoring rules

---

## Fixed

None in this release.

---

## Technical Details

### Files Changed
- `web_app/analyzer/views.py` - Added CTY file to download bundle, custom CTY upload handling
- `contest_tools/contest_definitions/cq_160.json` - CQ 160 contest definition
- `contest_tools/contest_specific_annotations/cq_160_parser.py` - CQ 160 parser
- `contest_tools/contest_specific_annotations/cq_160_scoring.py` - CQ 160 scoring
- `contest_tools/contest_specific_annotations/cq_160_multiplier_resolver.py` - CQ 160 multipliers
- `DevNotes/CQ_160_CW_PH_MODE_SUPPRESSION_DISCUSSION.md` - Discussion document
- `DevNotes/CTY_FILE_UPLOAD_IMPLEMENTATION.md` - Implementation notes
- `TECHNICAL_DEBT.md` - Added CQ 160 PH mode suppression entry

### Commits Included
- `Include CTY file in download bundle and document CQ 160 CW PH mode issue`
- `Add custom CTY file upload support with clear CUSTOM indicator`
- `Add CQ 160 Meter Contest support and enhance dashboard score reports`
- `feat(dashboard): eliminate cache dependency for contest definitions`

---

## Known Issues

### CQ 160 CW PH Mode in Breakdown Report
- **Issue:** PH mode appears in hourly breakdown report for CQ 160 CW when it shouldn't
- **Status:** Documented in Technical Debt and DevNotes
- **Impact:** Low - report functions correctly but shows unnecessary PH column for CW-only variant
- **Workaround:** None required - functional issue only
- **Related:** `DevNotes/CQ_160_CW_PH_MODE_SUPPRESSION_DISCUSSION.md`

---

## Migration Notes

No migration required. This is a feature enhancement release with no breaking changes.

Existing sessions and reports continue to work as before. New features (CQ 160 support, custom CTY upload) are optional and backward compatible.

---

## Documentation

- Added `DevNotes/CQ_160_CW_PH_MODE_SUPPRESSION_DISCUSSION.md` - Analysis and solution options for CQ 160 PH mode suppression
- Added `DevNotes/CTY_FILE_UPLOAD_IMPLEMENTATION.md` - CTY file upload implementation details
- Updated `TECHNICAL_DEBT.md` - Added CQ 160 CW PH mode suppression entry

---
