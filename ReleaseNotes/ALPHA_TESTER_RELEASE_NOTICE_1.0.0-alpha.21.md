# Alpha Release Notice: v1.0.0-alpha.21

**Release Date:** June 21, 2026  
**Version:** v1.0.0-alpha.21

---

## What's New

**Critical fix:** Missed multiplier **text reports generate again** after an alpha.20 regression (`UnboundLocalError` in pass-flag handling).

**Internal:** Multiplier dashboard charts now use shared partials and a common scaling helper (no intentional UI change).

---

## What This Means for You

- **If missed mult reports failed on alpha.20:** Update and re-run analysis; reports should generate normally.
- **Multiplier dashboard:** Should look and behave the same; please report any visual or export regressions.
- **No data migration** required.

---

## Testing Focus

We'd especially like feedback on:

1. **Missed multiplier text reports:** Confirm they generate on IARU-HF, WRTC, and other contests after alpha.20 failures.
2. **Pass flag `(P/...)`:** Still appears correctly for HQ, Officials, and DXCC where applicable.
3. **Multiplier dashboard:** Summary cards, band/mode spectrum tabs, screenshot export, and Sweepstakes progress bars unchanged.

---

## Update on Your VPS

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.21
docker compose up --build -d
```

See `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.21.md` for troubleshooting.
