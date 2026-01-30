# Release Announcement: v1.0.0-alpha.15

**Release Date:** January 30, 2026  
**Version:** `v1.0.0-alpha.15`

---

## Highlights

This release adds **QSO and Points options** for rate sheets and comparative rate sheets (filenames and dashboard), **CQ WPX public log** support, **cumulative difference plots for Points** on points-based contests, and clearer behavior for **CQ WPX** (multiplier dashboard hidden with an explicit "Not available" message).

---

## What's New

### Rate Sheets: QSO and Points
- For points-based contests, hourly rate sheets and comparative rate sheets are generated in both **QSO** and **Points** variants.
- On the QSO Dashboard **Rate Detail** tab you can choose **Comparison (QSOs)** or **Comparison (Points)** when comparing multiple logs; single-log rate sheets use the same naming convention.

### Cumulative Difference: QSOs and Points
- On points-based contests, cumulative difference reports are available for both QSOs and Points.
- The **Rate Differential** card on the QSO Dashboard has a **QSOs | Points** toggle to switch between the two.

### CQ WPX Support
- You can fetch **CQ WPX** public logs (CW and SSB) from the web app; the main dashboard is fully available for WPX.
- The **Multiplier Reports** dashboard is not used for WPX; the main dashboard hides that card for WPX, and opening the multiplier dashboard directly for a WPX session shows "Not available for this contest."

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.15.md) for complete technical details, file changes, and commit history.

---
