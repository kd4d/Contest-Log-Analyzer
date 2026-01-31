# Release Notes: v1.0.0-alpha.18

**Release Date:** January 31, 2026  
**Tag:** `v1.0.0-alpha.18`

**Note:** These release notes cover changes on the feature branch since `v1.0.0-alpha.17`.

---

## Summary

This release adds the **Rate Chart** report (QSO or Points rate as a grouped bar chart for 1-3 logs), a **Bar Graph** option in the QSO Dashboard **Rate Differential** pane alongside Cumulative Difference, and fixes for **Cumulative Difference** plots: a hard cap of 15 horizontal grid lines with shared axes, overflow/infinity handling in axis math, and fixed-size + scrollable rendering in the Rate Differential pane so the summary table below the plot is no longer truncated. Contest definitions now include mode in the name for single-mode contests. QSO Dashboard and AI agent rules/checklists were updated; temporary diagnostic log messages were removed.

---

## Added

### Rate Chart Report
- **Report:** New plot report showing QSO or Points rate (hourly) as a grouped bar chart for 1-3 logs. Available from report manifest and dashboards where rate data is shown.
- **Metrics:** QSOs or Points (on points-based contests). Band and mode filters apply.
- **Layout:** Bars touch within each hour (no gap); vertical grid lines in gaps between hours. Same styling as other rate/chart reports.

### Bar Graph in Rate Differential Pane
- **QSO Dashboard (Pairwise Strategy):** Rate Differential card now has two plot-type options: **Cumulative Difference** (existing) and **Bar Graph** (new). Bar Graph shows the same Rate Chart report used elsewhere. Toggle between QSOs/Points and band (or mode) as before.

---

## Changed

### Contest Definitions (Single-Mode)
- Contest definition names for single-mode contests now include the mode (e.g. CQ 160 CW, CQ 160 SSB, ARRL SS CW, ARRL SS PH, NAQP CW/PH/RTTY). Improves clarity in selectors and report labels.

### Report Drawer and Overlay
- Report drawer (report list sidebar) now triggers the report overlay correctly when a report link is clicked; overlay and drawer behavior aligned with navigation.

### QSO Dashboard and Progress
- QSO dashboard fixes and progress handling improvements. AI agent rules and checklists updated for commit workflow and release preparation.

---

## Fixed

### Cumulative Difference Plots
- **Grid lines:** Hard cap of 15 horizontal grid lines enforced; step and range recomputed when expansion would exceed 15. Both Y-axes (cumulative and hourly) share the same N grid lines.
- **Overflow/infinity:** Axis math now caps `target_ratio` and guards `cumul_max`, `cumul_range_raw`, and related values so non-finite values do not cause runtime errors or "cannot convert float infinity to integer."
- **Rate Differential pane (dashboard):** Cumulative Difference plot in the QSO Dashboard Rate Differential card now uses the same fixed-size + scrollable viewport approach as the Band Activity (butterfly) chart. The figure renders at design size; the card body provides a fixed-height scrollable area so the summary table below the plot is fully visible (no truncation).

### Diagnostics
- Removed temporary QSO Dashboard diagnostic `logger.warning` messages (contest name, valid_bands, valid_modes, is_single_band, diff_selector_type). Operational warnings for missing report files are unchanged.

---

## Technical Details

### Files Changed / Added
- `contest_tools/reports/plot_cumulative_difference.py` – N_MAX=15 enforced with while-loop; target_ratio and cumul_max/cumul_range_raw guarded for finite values; same N for both axes.
- `contest_tools/reports/chart_rate.py` – Rate Chart report (grouped bar, 1-3 logs; bars touch within hour, vertical lines in gaps).
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` – Rate Differential pane: chart-diff uses fixed-size + scrollable wrapper (same as chart-band-activity); Bar Graph option and toggle wiring.
- `web_app/analyzer/views.py` – Rate Chart wiring for QSO dashboard; removal of QSO Dashboard diagnostic logs.
- `contest_tools/contest_definitions/*.json` – Single-mode contest names include mode where applicable.
- `Docs/AI_AGENT_RULES.md`, `Docs/AI_AGENT_CHECKLISTS.md` – Commit workflow, release preparation, and checklists.

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. Existing sessions and reports continue to work. Rate Chart appears in report lists where rate data is available. Rate Differential pane shows both Cumulative Difference and Bar Graph; Cumulative Difference table is visible via scroll when the card is narrow.

---

## Documentation

- CHANGELOG.md updated with [1.0.0-alpha.18].
- Release notes and Release Announcement added for v1.0.0-alpha.18.
- Docs version references to be updated to v1.0.0-alpha.18 in version-bump commit.

---

## Commits Included

- chore(analyzer): remove QSO Dashboard diagnostic log messages
- Contest definitions: include mode in name for single-mode contests
- QSO dashboard fixes, progress handling, and AI agent rules
- fix(reports): cumulative difference plot grid cap and table display
- feat(analyzer): add Bar Graph option to Rate Differential pane
- feat(analyzer): add report drawer trigger to overlay for report navigation
- Rate Chart: touch bars within hour (bargroupgap=0), vertical lines in gaps only
- Add Rate Chart report (QSO/Point rate, grouped bar, 1-3 logs)
