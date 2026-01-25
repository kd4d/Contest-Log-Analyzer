# Release Notes: v1.0.0-alpha.12

**Release Date:** January 27, 2026  
**Tag:** `v1.0.0-alpha.12`

**Note:** These release notes include all changes from the feature branch `feature/1.0.0-alpha.12` merged to master, plus any commits made directly to master since `v1.0.0-alpha.11`.

---

## Summary

This release fixes a critical scoring bug in ARRL DX contests where US/VE station scores were calculated as exactly twice the correct value. The issue was caused by the StandardCalculator not filtering multiplier rules by the `applies_to` field, resulting in both DXCC and STPROV multipliers being counted for W/VE stations. This release also fixes location type determination for Alaska, Hawaii, and US possessions to correctly classify them as DX stations.

---

## Fixed

### ARRL DX Scoring - Critical 2x Multiplier Bug
- **Fixed StandardCalculator to filter multiplier rules by applies_to field**
  - StandardCalculator now respects the `applies_to` field in multiplier rules
  - Matches the logic used in ScoreStatsAggregator for consistency
  - Only processes multiplier rules applicable to the log's location type
  - **Impact:** ARRL DX CW/SSB scores for US/VE stations now correct (previously 2x)
  - **Impact:** ARRL DX CW/SSB scores for DX stations now correct (previously 2x)

### ARRL DX Location Type Determination
- **Fixed arrl_dx_location_resolver to correctly classify Alaska/Hawaii as DX**
  - Now checks DXCCPfx (KH6, KL7, CY9, CY0) before checking DXCCName
  - Alaska, Hawaii, St. Paul Is., and Sable Is. now correctly treated as DX stations
  - Consistent with official ARRL DX contest rules

### ARRL DX Scoring Module
- **Fixed arrl_dx_scoring to use consistent location type logic**
  - Uses same prefix-checking logic as location resolver
  - Ensures scoring uses correct location type determination
  - Prevents scoring inconsistencies

---

## Added

### Documentation
- **Added AI agent operation checklists and maintenance rules**
  - New file: `Docs/AI_AGENT_CHECKLISTS.md`
  - Comprehensive checklists for common operations
  - Maintenance rules and guidelines for AI agents

---

## Technical Details

### Files Changed
- `contest_tools/score_calculators/standard_calculator.py` - Added applies_to filtering logic
- `contest_tools/contest_specific_annotations/arrl_dx_location_resolver.py` - Fixed prefix checking
- `contest_tools/contest_specific_annotations/arrl_dx_scoring.py` - Fixed location type determination
- `Docs/AI_AGENT_CHECKLISTS.md` - New AI agent checklists
- `Docs/AI_AGENT_RULES.md` - Added maintenance rules

### Commits Included
- Fix ARRL DX scoring: Correct 2x multiplier issue for US/VE stations
- feat: add AI agent operation checklists and maintenance rule

### Root Cause Analysis
The StandardCalculator (default time-series score calculator) was processing ALL multiplier rules without filtering by the `applies_to` field. For ARRL DX:
- W/VE operators should only count DXCC multipliers (`applies_to: "W/VE"`)
- DX operators should only count STPROV multipliers (`applies_to: "DX"`)
- StandardCalculator was counting both rules for all operators, causing 2x multiplier counts and 2x scores

The fix adds filtering logic that matches ScoreStatsAggregator, ensuring only applicable multiplier rules are processed based on the log's location type.

### Verification
- All 19 contest definitions checked - only ARRL DX has `applies_to` fields
- All other contests using StandardCalculator are unaffected (no `applies_to` fields)
- Contests with custom calculators (WAE, NAQP, WRTC) are unaffected
- Edge cases handled (None values, missing location types)

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. This is a bug fix release with no breaking changes.

**Important:** If you have previously analyzed ARRL DX logs (CW or SSB), you should re-analyze them to get correct scores. The previous scores were exactly 2x the correct value for US/VE stations.

Existing sessions and reports continue to work as before. The fix is automatically applied to all new analyses.

---

## Documentation

- Added AI agent operation checklists and maintenance rules
- Updated release workflow documentation

---
