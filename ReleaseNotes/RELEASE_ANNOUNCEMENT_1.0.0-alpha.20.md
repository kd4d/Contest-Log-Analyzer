# Release Announcement: v1.0.0-alpha.20

**Release Date:** June 18, 2026  
**Version:** `v1.0.0-alpha.20`

---

## Highlights

Missed multiplier text reports now show a **(P/...) pass flag** for **HQ Stations**, **IARU Officials**, and **DXCC** when the same multiplier was worked on another band within 2 minutes before the first QSO on the current band (e.g. `(P/Run/CW) 2`). Production hosting documentation for **Hostinger** (`cla.kd4d.org`) and **nginx 504** troubleshooting during long analyses are also included.

---

## What's New

### Missed Multipliers Pass Flag
- `(P/Run)` / `(P/S&P)` or `(P/Run/CW)` marks a passed multiplier on per-band tables.
- HQ, Officials, and DXCC only; zones unchanged.

### Operations Documentation
- Hostinger VPS install path, Docker Manager access, and update commands.
- nginx `proxy_read_timeout` guidance when uploads fail at the Generating step.

---

## VPS Update

See [VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.20.md](VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.20.md).

---

## For More Details

See the [Full Release Notes](RELEASE_NOTES_1.0.0-alpha.20.md) for complete technical details and file changes.
