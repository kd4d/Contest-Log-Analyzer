# Release Announcement: v1.0.0-alpha.12

**Release Date:** January 27, 2026  
**Version:** `v1.0.0-alpha.12`

---

## Highlights

This release fixes a **critical scoring bug** in ARRL DX contests where US/VE station scores were calculated as exactly twice the correct value. The issue affected both ARRL DX CW and ARRL DX SSB contests.

---

## Important Fixes

### ARRL DX Scoring Bug (Critical)
**Fixed 2x scoring issue for ARRL DX contests**

- US/VE station scores were previously calculated as exactly 2x the correct value
- DX station scores were also affected (2x multiplier count)
- **Root cause:** StandardCalculator was counting both DXCC and STPROV multipliers for all operators
- **Fix:** StandardCalculator now correctly filters multipliers based on operator location type
  - W/VE operators: Only DXCC multipliers count
  - DX operators: Only STPROV multipliers count

**Action Required:** If you have previously analyzed ARRL DX logs, please re-analyze them to get correct scores.

### Location Type Classification
**Fixed Alaska, Hawaii, and US possessions classification**

- Alaska (KL7), Hawaii (KH6), St. Paul Is. (CY9), and Sable Is. (CY0) are now correctly classified as DX stations
- Consistent with official ARRL DX contest rules
- Ensures correct scoring for these special cases

---

## Improvements

- Enhanced AI agent documentation with operation checklists and maintenance rules

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.12.md) for complete technical details, file changes, and commit history.

---
