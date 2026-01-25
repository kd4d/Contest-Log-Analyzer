# Release Announcement: v1.0.0-alpha.11

**Release Date:** January 24, 2026  
**Version:** `v1.0.0-alpha.11`

---

## Highlights

This release introduces **multiplier timeline reports** for tracking multiplier acquisition over time, implements **Sweepstakes contest-wide QSO breakdown visualization** to fix misleading band-by-band displays, and includes several important bug fixes and improvements.

---

## New Features

### Multiplier Timeline Reports
Track when multipliers were first worked during the contest. Available for both single-log analysis and multi-log comparisons, showing the hourly progression of unique multipliers.

### Sweepstakes Contest-Wide QSO Breakdown
For ARRL Sweepstakes contests, the dashboard now shows contest-wide QSO breakdown (not band-by-band) since QSOs count once per contest. This fixes misleading visualizations that implied QSOs were counted per band.

---

## Important Fixes

### CQ 160 Multiplier Detection
Fixed multiplier detection for CQ 160 contest, including proper handling of IG9/IH9 prefixes and multiplier filtering rules.

### WRTC Scoring
Fixed scoring calculation for WRTC contests and improved the user interface for WRTC contest selection.

### Report Improvements
- Suppressed redundant detail sections for single-mode contests
- Removed unnecessary columns from single-log multiplier breakdown reports
- Improved error handling and warning messages

---

## Improvements

- Enhanced diagnostic logging (now visible at default log level)
- Better error messages and pandas FutureWarning fixes
- Improved Docker build performance (reduced image size)
- Updated supported contests documentation (ARRL 10 Meter now listed)

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.11.md) for complete technical details, file changes, and commit history.

---
