# Release Notes: v1.0.0-alpha.15

**Release Date:** January 30, 2026  
**Tag:** `v1.0.0-alpha.15`

**Note:** These release notes include all changes from the feature branch `feature/1.0.0-alpha.15` merged to master, plus any commits made directly to master since `v1.0.0-alpha.14`.

---

## Summary

This release adds QSO and Points variants for rate sheets and comparative rate sheets (matching dashboard options and filenames), CQ WPX public log fetcher support, cumulative difference plots for Points on points-based contests, and hides the Multiplier Reports dashboard for CQ WPX contests (with an explicit "Not available" message when accessing the multiplier dashboard directly).

---

## Added

### Rate Sheets and Comparative Rate Sheets: QSO and Points Variants
- **Hourly Rate Sheet (`rate_sheet`)**: For points-based contests, generates both QSO and Points variants.
  - Filenames: `rate_sheet_qsos--{callsign}.txt`, `rate_sheet_points--{callsign}.txt`.
  - Dashboard: Rate Detail dropdown shows per-log rate sheets (QSO variant discovered by default).
- **Comparative Rate Sheet (`rate_sheet_comparison`)**: For points-based contests, generates both QSO and Points variants.
  - Filenames: `rate_sheet_comparison_qsos--{callsigns}.txt`, `rate_sheet_comparison_points--{callsigns}.txt`.
  - Dashboard: Rate Detail dropdown offers "Comparison (QSOs)" and "Comparison (Points)" when both exist; legacy single-file format still supported.

### Cumulative Difference Plots: Points Variant
- For contests using points-based scoring (`total_points` or `points_times_mults`), cumulative difference reports are generated for both QSOs and Points.
- QSO Dashboard: Rate Differential card includes a **QSOs | Points** toggle to switch between the two metrics.

### CQ WPX Public Log Fetcher
- Public log retrieval for CQ WPX CW and CQ WPX SSB contests from https://cqwpx.com/publiclogs/.
- Home page contest selector includes "CQ WPX" with year and mode (CW/SSB) selection; full dashboard available for WPX analyses.

### Multiplier Dashboard Behavior for CQ WPX
- Main dashboard hides the "Multiplier Reports" card for CQ WPX contests (WPX does not use country/zone multiplier reports in the same way).
- Direct link to Multiplier Dashboard for a WPX session shows a dedicated "Not available for this contest" page instead of an empty or incorrect dashboard.

---

## Changed

### Time Series Data
- Hourly aggregates now include `by_band_points` and `by_mode_points` (and `points` list) for points-based contests, enabling Points variants of rate sheet and comparison reports.

### Documentation
- Updated version references across documentation to v1.0.0-alpha.15.
- Report Interpretation Guide: Rate sheet and comparative rate sheet sections updated to describe QSO/Points filename variants and dashboard options; cumulative difference section updated to describe Points variant and QSOs/Points toggle.

---

## Technical Details

### Files Changed (representative)
- `contest_tools/data_aggregators/time_series.py` – Hourly points-by-band/mode.
- `contest_tools/reports/text_rate_sheet.py` – QSO/Points metric loop and filenames.
- `contest_tools/reports/text_rate_sheet_comparison.py` – QSO/Points variants and filenames.
- `contest_tools/reports/plot_cumulative_difference.py` – Points variant for points-based contests.
- `contest_tools/utils/log_fetcher.py` – CQ WPX public log fetcher.
- `web_app/analyzer/views.py` – Rate sheet/comparison discovery (qsos/points), WPX dashboard and multiplier unavailable.
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` – Rate Detail comparison QSO/Points options; Rate Differential QSOs/Points toggle.
- `web_app/analyzer/templates/analyzer/dashboard.html` – Hide multiplier card for WPX.
- `web_app/analyzer/templates/analyzer/multiplier_dashboard_unavailable.html` – New template for WPX multiplier dashboard.
- `web_app/analyzer/templates/analyzer/home.html` – CQ WPX contest option and year/mode.

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. New report filenames are additive; legacy rate sheet and comparison filenames remain supported for discovery. Existing sessions and reports continue to work.

---

## Documentation

- Updated version references across all documentation files to match project release v1.0.0-alpha.15.
- Report Interpretation Guide: Added QSO/Points variants and dashboard behavior for rate sheet, comparative rate sheet, and cumulative difference plots.

---
