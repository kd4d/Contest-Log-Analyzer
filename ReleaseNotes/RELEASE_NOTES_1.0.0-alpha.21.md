# Release Notes: v1.0.0-alpha.21

**Release Date:** June 21, 2026  
**Tag:** `v1.0.0-alpha.21`

**Note:** These release notes cover changes since `v1.0.0-alpha.20`.

---

## Summary

This release **fixes missed multiplier text report generation** (an alpha.20 regression that raised `UnboundLocalError` in `get_missed_data()`). It also **refactors the multiplier dashboard** chart markup into shared templates and a common Python helper for layout/scaling (no intentional user-visible UI change).

---

## Fixed

### Missed Multipliers Report Generation
- **`UnboundLocalError` in `get_missed_data()`:** `show_pass_flag` referenced `detect_pass` before it was assigned when building `full_results`, which prevented **all** missed multiplier text reports from generating after alpha.20.
- **Fix:** Assign `detect_pass` before constructing `full_results`.

---

## Changed

### Multiplier Dashboard (Internal Refactor)
- Summary cards and band/mode spectrum charts moved to shared partials:
  - `contest_tools/templates/partials/multiplier_breakdown_summary.html`
  - `contest_tools/templates/partials/multiplier_breakdown_spectrum.html`
- Chart layout, multiplier tab visibility, spectrum scaling, and Sweepstakes extras centralized in `contest_tools/utils/multiplier_dashboard_utils.py`.
- `multiplier_dashboard` view uses `build_multiplier_breakdown_chart_context()` instead of duplicated inline logic.

---

## Added

None in this release.

---

## Technical Details

### Key Files
- `contest_tools/data_aggregators/multiplier_stats.py` – pass-flag assignment order fix.
- `contest_tools/utils/multiplier_dashboard_utils.py` – shared breakdown chart context.
- `contest_tools/templates/partials/multiplier_breakdown_*.html` – shared dashboard partials.
- `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` – includes partials; duplicate inline markup removed.
- `web_app/analyzer/views.py` – uses shared chart context helper.

---

## Known Issues

None in this release.

---

## Migration Notes

No database migration required. Regenerate missed multiplier text reports if alpha.20 failed to produce them.

---

## Documentation

- CHANGELOG.md updated with [1.0.0-alpha.21].
- Release notes, announcement, alpha tester notice, and VPS update instructions added for v1.0.0-alpha.21.
