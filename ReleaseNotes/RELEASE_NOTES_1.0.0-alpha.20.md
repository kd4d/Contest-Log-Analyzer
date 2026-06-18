# Release Notes: v1.0.0-alpha.20

**Release Date:** June 18, 2026  
**Tag:** `v1.0.0-alpha.20`

**Note:** These release notes cover changes since `v1.0.0-alpha.19`.

---

## Summary

This release adds the **(P/...) pass flag** in missed multiplier text reports for **HQ Stations**, **IARU Officials**, and **DXCC** country multipliers when the same value was worked on another band within 2 minutes before the first QSO on the current band. It also documents **Hostinger production hosting** (`cla.kd4d.org`) and **nginx 504 Gateway Timeout** troubleshooting during long report generation.

---

## Added

### Missed Multipliers: Pass Flag (P/)
- Per-band missed-multiplier cells show `(P/Run)`, `(P/S&P)`, or multi-mode `(P/Run/CW)` when the multiplier was **passed** from another band (same log, within 2 minutes before the first QSO on that band).
- Applies to `Mult_HQ`, `Mult_Official`, and `Mult_DXCC` — not zones.
- Report footnote explains `(P/...)` when any pass flags appear in the table.
- In-app help documents the pass flag.

### Documentation
- **Installation Guide Section 3.0:** Hostinger VPS production hosting (`srv1269198`, `/docker/Contest-Log-Analyzer`, Docker Manager access).
- **nginx troubleshooting:** 504 Gateway Timeout during report generation (`proxy_read_timeout` / `proxy_send_timeout`).
- **README:** pointer to Hostinger production section.

---

## Changed

- **AI agent rules:** VPS instruction template includes Hostinger production table and Installation Guide link.

---

## Fixed

None reported for this release.

---

## Technical Details

### Key Files
- `contest_tools/data_aggregators/multiplier_stats.py` – pass detection (`_is_pass_from_other_band`, `_annotate_pass_flags`).
- `contest_tools/utils/report_utils.py` – `P/` prefix in cell formatter and slot width.
- `contest_tools/reports/text_missed_multipliers.py` – pass-flag footnote.
- `Docs/InstallationGuide.md` – Hostinger and nginx sections.

---

## Known Issues

None in this release.

---

## Migration Notes

No database migration required. Regenerate missed multiplier text reports on IARU-HF or WRTC comparisons to see `(P/...)` cells where pass conditions apply.

---

## Documentation

- CHANGELOG.md updated with [1.0.0-alpha.20].
- Release notes, announcement, alpha tester notice, and VPS update instructions added for v1.0.0-alpha.20.
