# Alpha Release Notice: v1.0.0-alpha.19

**Release Date:** June 18, 2026  
**Version:** v1.0.0-alpha.19

---

## What's New

This release improves **missed multiplier text reports** for multi-mode contests. When one report covers all modes (e.g. IARU-HF, WRTC), table cells now show **aligned** Run/S&P and mode labels such as `(Run/CW) 2` and `(S&P/PH) 1`. Per-mode reports (e.g. ARRL 10) still use `(Run)` / `(S&P)` because mode is already in the report title.

Also included: **ARRL Sweepstakes** public log download, **Run/S&P algorithm** doc updates, and RBN/IARU archive download tooling.

---

## What This Means for You

- **Existing sessions:** Regenerate missed multiplier text reports to see the new cell format on multi-mode contests.
- **No upgrade steps required** beyond the normal VPS update (see VPS update instructions).
- All other dashboards and reports behave as before.

---

## Testing Focus

We'd especially like feedback on:

1. **Missed multipliers (IARU-HF / WRTC):** Do the aligned mode slots read clearly? Are column widths reasonable?
2. **ARRL 10 (per-mode):** Confirm cells still show `(Run)` / `(S&P)` without redundant mode labels.
3. **Sweepstakes public log fetch:** Does download work for your year/mode selection?

---

## Update on Your VPS

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.19
docker compose up --build -d
```

See `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.19.md` for troubleshooting.
