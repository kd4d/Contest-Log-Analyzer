# Release Announcement: v1.0.0-alpha.18

**Release Date:** January 31, 2026  
**Version:** `v1.0.0-alpha.18`

---

## Highlights

This release adds the **Rate Chart** report (grouped bar chart of QSO or Points rate for 1-3 logs) and a **Bar Graph** option in the QSO Dashboard **Rate Differential** pane. **Cumulative Difference** plots are improved: at most 15 horizontal grid lines, both axes share the same grid, and the summary table below the plot is no longer truncated in the dashboard (fixed-size + scroll). Contest definitions now include mode in the name for single-mode contests (e.g. CQ 160 CW, ARRL SS PH). Temporary diagnostic log messages were removed.  Public Log Download for Sweepstakes added.

---

## What's New

### Rate Chart Report
- **New report:** Hourly QSO or Points rate as a grouped bar chart for 1-3 logs. Available from the report list and dashboards where rate data is shown.
- **Metrics:** QSOs or Points (on points-based contests). Band and mode filters apply.
- **Layout:** Bars touch within each hour; vertical grid lines between hours.

### Rate Differential Pane (QSO Dashboard)
- **Bar Graph option:** Toggle between **Cumulative Difference** and **Bar Graph** in the Rate Differential card (Pairwise Strategy tab). Bar Graph shows the same Rate Chart report.
- **Cumulative Difference table:** The summary table below the Cumulative Difference plot is now fully visible in the dashboard. The card uses a fixed-height scrollable area (same approach as the Band Activity butterfly chart) so the table is never truncated.

### Cumulative Difference Plots
- **Grid lines:** Maximum of 15 horizontal grid lines; both Y-axes (cumulative and hourly) share the same grid. Axis math is guarded so extreme data no longer causes overflow or "cannot convert float infinity to integer" errors.

### Contest Definitions
- **Single-mode contests:** Names now include the mode (e.g. CQ 160 CW, CQ 160 SSB, ARRL SS CW, ARRL SS PH, NAQP CW/PH/RTTY) for clearer selectors and labels.

### Sweepstakes Public Log Downloads

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.18.md) for complete technical details and file changes.

---
