# WRTC Propagation Mockups (24 hourly charts + spider diagrams)

Generated from `GB9WR_processed.csv` using `scripts/wrtc_propagation_mockup.py`.

## Bar charts (root of this folder)

- **One chart per contest hour** (1–24, UTC).
- **Five band clusters** on the x-axis: 80M, 40M, 20M, 15M, 10M.
- **16 grouped bars per band**: 8 regions × 2 modes (CW, PH), ordered by region then mode.
- **Bar height** = points (2 for Europe, 5 for others; WRTC scoring).
- **Regions**: Europe, Japan, Other Asia, Middle East, Africa, North America, South America, Oceania.
- **Movie**: `wrtc_propagation_movie.html` — hour slider, play/pause, configurable seconds per frame.

## Spider diagrams (`spider/` subdirectory)

- **24 individual images**: one HTML per contest hour, each with **five spider (radar) plots** in two rows (80M, 40M, 20M on row 1; 15M, 10M on row 2).
- **Spokes** = 8 regions; **radius** = points/3 (data-space scaling).
- **Angles** = approximate beam headings from Eastern GB (Europe 0°, Japan 35°, Other Asia 80°, etc.).
- **Movie**: `spider/wrtc_spider_movie.html` — same controls as bar movie (UTC hour slider, play/pause, seconds per frame); no auto-play.

## Regenerate

From the repo root, using the `cla` environment (Plotly required):

```bash
C:\Users\mbdev\miniforge3\envs\cla\python.exe scripts/wrtc_propagation_mockup.py "path\to\processed.csv"
```

Optional second argument: output directory (default: `wrtc_propagation_mockups/`).
