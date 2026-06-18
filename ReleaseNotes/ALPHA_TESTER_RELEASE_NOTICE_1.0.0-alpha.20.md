# Alpha Release Notice: v1.0.0-alpha.20

**Release Date:** June 18, 2026  
**Version:** v1.0.0-alpha.20

---

## What's New

Missed multiplier text reports add a **(P/...) pass flag** for **HQ Stations**, **IARU Officials**, and **DXCC** country multipliers. When the same value was worked on **another band within 2 minutes** before the first QSO on the current band, cells show `(P/Run)`, `(P/S&P)`, or multi-mode `(P/Run/CW)` instead of the plain Run/S&P label.

Also included: **Hostinger production** documentation for `cla.kd4d.org` and **nginx 504** troubleshooting when analysis times out at Generating.

---

## What This Means for You

- **Existing sessions:** Regenerate missed multiplier text reports on IARU-HF or WRTC comparisons to see `(P/...)` where applicable.
- **VPS operators:** See updated Installation Guide Section 3.0 if you host on Hostinger or hit 504 timeouts during upload/analysis.
- **No data migration** required.

---

## Testing Focus

We'd especially like feedback on:

1. **IARU-HF / WRTC missed mult reports:** Do `(P/...)` flags appear where you expect (cross-band passes within ~2 minutes)?
2. **HQ vs DXCC vs Officials:** Confirm pass flag on the right multiplier types only (not zones).
3. **Column alignment:** Multi-mode aligned slots still align with `P/` prefix.

---

## Update on Your VPS

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.20
docker compose up --build -d
```

See `ReleaseNotes/VPS_UPDATE_INSTRUCTIONS_1.0.0-alpha.20.md` for troubleshooting.
