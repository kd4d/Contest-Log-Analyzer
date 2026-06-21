# Release Announcement: v1.0.0-alpha.21

**Release Date:** June 21, 2026  
**Version:** `v1.0.0-alpha.21`

---

## Highlights

**Missed multiplier text reports work again.** Alpha.20 introduced a bug that blocked generation of all missed multiplier reports; this release fixes that regression. The multiplier dashboard also received an internal refactor (shared chart partials) with no intentional UI change.

---

## Important Fix

### Missed Multipliers Reports
- If missed multiplier text reports failed to generate after updating to alpha.20, update to alpha.21 and re-run analysis.
- Root cause: `UnboundLocalError` when building pass-flag data for HQ, Officials, and DXCC multipliers.

---

## Improvements

### Multiplier Dashboard (Maintainability)
- Chart markup and scaling logic consolidated for easier future updates to the HTML breakdown report and web dashboard.

---

## VPS Update

See [VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.21.md](VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.21.md).

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.21.md) for complete technical details and file changes.
