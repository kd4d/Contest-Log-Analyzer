# Release Notes: v1.0.0-alpha.17

**Release Date:** January 30, 2026  
**Tag:** `v1.0.0-alpha.17`

**Note:** These release notes cover changes on the feature branch since `v1.0.0-alpha.16`.

---

## Summary

This release adds a **Report manifest drawer** (persistent off-canvas sidebar) on the main dashboard, QSO dashboard, and multiplier dashboard. A pull-out arrow on the left side (vertically centered) opens a hierarchical list of generated reports that matches the ZIP download structure. Clicking a report opens it in the existing full-screen overlay. The list uses actual filenames (callsign and band when present in the filename); JSON files are excluded; reports not in the defined structure appear under a "Miscellaneous" section. The drawer includes search filter, category collapse, active-report highlight, and closes via Escape or clicking the scrim.

---

## Added

### Report Manifest Drawer (Report List Sidebar)
- **Trigger:** A pull-out chevron (arrow) on the left edge of the viewport, vertically centered. Click to open the drawer; no overlap with the main navigation.
- **Content:** Hierarchical list of generated reports in categories: Single Log Reports, Comparison Reports, Multiplier Reports, QSO / Contest-wide, Miscellaneous (undefined reports), and Bulk Actions (Download All). Same set of reports as included in the ZIP download (viewable .txt and .html only; JSON excluded).
- **Labels:** Each report is shown by its actual filename (basename without extension), so callsign and band information appear when present in the filename (e.g. `rate_sheet_qsos--k3lr`, `qso_rate_plots_20m--k3lr_w3lpl`).
- **Behavior:** Clicking a report link opens it in the existing full-screen report overlay (same as the "popout" buttons on the dashboards). The drawer closes after selection. "Download All (.zip)" scrolls to and focuses the existing Download All button.
- **UX:** Search box filters the list by category or filename. Categories can be collapsed/expanded. The currently open report is highlighted in the list. Close via the X button, clicking outside (scrim), or Escape.

---

## Technical Details

### Files Changed / Added
- `web_app/analyzer/views.py` – Added `_REPORT_CATEGORIES`, `_report_display_label()`, `_build_report_manifest_tree()`; pass `report_manifest_tree` and `session_id` from `dashboard_view`, `qso_dashboard`, `multiplier_dashboard`. Exclude JSON from drawer list; use basename (no extension) as label; "Miscellaneous" for undefined reports.
- `web_app/analyzer/templates/analyzer/partials/report_drawer.html` – New partial: trigger (chevron, left, centered), scrim, panel with header, search, accordion categories, report links (`.report-overlay-link`), Bulk Actions with Download All.
- `web_app/analyzer/static/js/report_drawer.js` – New: open/close drawer, search filter, category collapse, active-report highlight (via `report-overlay-open` event), Escape/scrim close, Download All trigger.
- `web_app/analyzer/static/js/report_overlay.js` – Dispatch `report-overlay-open` with `href` when opening a report so the drawer can highlight the active link.
- `web_app/analyzer/templates/analyzer/dashboard.html`, `qso_dashboard.html`, `multiplier_dashboard.html` – Include report drawer partial and script when `report_manifest_tree` is present.

---

## Known Issues

None in this release.

---

## Migration Notes

No migration required. Existing sessions and reports continue to work. The drawer appears on main, QSO, and multiplier dashboards when a session has a report manifest; no configuration needed.

---

## Documentation

- CHANGELOG.md updated with [1.0.0-alpha.17].
- Release notes, Alpha Tester Notice, and Release Announcement added for v1.0.0-alpha.17.
- In-app help (Dashboard Help) updated with Report List (drawer) section.
- Docs version references updated to v1.0.0-alpha.17 where applicable.

---
