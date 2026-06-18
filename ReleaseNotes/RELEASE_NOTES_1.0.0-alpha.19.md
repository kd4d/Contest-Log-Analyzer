# Release Notes: v1.0.0-alpha.19

**Release Date:** June 18, 2026  
**Tag:** `v1.0.0-alpha.19`

**Note:** These release notes cover changes since `v1.0.0-alpha.18`.

---

## Summary

This release adds **mode + Run/S&P breakdown** in missed multiplier text reports for multi-mode contests (e.g. IARU-HF, WRTC), with **fixed-width aligned mode slots** in table cells. It also adds **ARRL Sweepstakes public log archive** download support, **Run/S&P algorithm documentation** updates, an **RBN download script** with IARU 2025 daily archives, and release-process documentation improvements.

---

## Added

### Missed Multipliers: Mode + Run/S&P (Text Reports)
- **Multi-mode all-modes reports** (IARU-HF, WRTC, etc.): cells show aligned slots such as `(Run/CW) 2` and `(S&P/PH) 1` using PH labels.
- **Per-mode reports** (e.g. ARRL 10): cells remain `(Run) 3` / `(S&P) 1` because mode is already in the report title.
- **Column alignment:** fixed-width slots per `valid_modes` order so mode labels align across rows.

### Public Log Archive
- **ARRL Sweepstakes CW/SSB:** public log fetch from the ARRL archive (complements existing archive contests).

### Tooling
- **RBN download script** and IARU 2025 daily zip archive support for propagation/RBN data workflows.

---

## Changed

### Documentation
- **Run/S&P algorithm spec** (`Docs/RunS&PAlgorithm.md`): Pass 1/2 window and exclusion rules clarified.
- **AI agent rules and checklists:** release workflow and commit guidance updates.
- **In-app help:** missed multipliers section documents multi-mode cell notation.
- WRTC propagation prototype documentation moved out of the web app repo path.

---

## Fixed

None reported for this release.

---

## Technical Details

### Key Files
- `contest_tools/utils/report_utils.py` – `show_mode_in_missed_cells`, `format_missed_mult_cell`, slot width helpers.
- `contest_tools/data_aggregators/multiplier_stats.py` – per-mode aggregation in `get_missed_data`.
- `contest_tools/reports/text_missed_multipliers.py` – aligned cell formatting via PrettyTable.
- `contest_tools/utils/log_fetcher.py` – ARRL Sweepstakes archive support (from prior branch commits).
- `Docs/RunS&PAlgorithm.md` – algorithm documentation enhancements.

---

## Known Issues

None in this release.

---

## Migration Notes

No database migration required. Regenerate missed multiplier text reports to see mode + Run/S&P slots on multi-mode contests.

---

## Documentation

- CHANGELOG.md updated with [1.0.0-alpha.19].
- Release notes, announcement, and VPS update instructions added for v1.0.0-alpha.19.
