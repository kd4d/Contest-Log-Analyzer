**Version:** 2026.01.05-Beta-2
**Status:** Phase 3 Execution

## Phase 3: The Web Pathfinder (Current)
**Goal:** Transition from a local CLI tool to a stateless, containerized Web Dashboard.
**Core Constraint:** The web container (`web-1`) is lightweight. It lacks `matplotlib`, `kaleido`, and `ffmpeg`.

### 1. Visualization Architecture (Stabilization Complete)
* [x] **Adopt Plotly:** All new charts must use `plotly` for HTML/JS rendering.
* [x] **Deprecate Backend PNGs:** Removed `fig.write_image()` calls from all core and legacy reports.
* [x] **Client-Side Capture:** Configured `toImageButtonOptions` to ensure clean filenames for client-side downloads.

### 2. The Data Abstraction Layer (DAL)
* [x] **Decoupling:** Reports must not calculate data. They must request data from `data_aggregators`.
* [x] **WORM Strategy:** Expensive calculations (Matrix, Breakdown) are run once during ingestion (`analyze_logs`) and serialized to JSON artifacts (`json_multiplier_breakdown`).
* [x] **Hydration:** The Dashboard hydrates views from these JSON artifacts, bypassing `LogManager` parsing on page load.

### 3. Report Modernization Status
| Report ID | Status | Action Required |
| :--- | :--- | :--- |
| `chart_comparative_activity_butterfly` | **ACTIVE** | Logic verified (MatrixAggregator). Config fixed. |
| `plot_wrtc_propagation` | **ACTIVE** | PNG gen removed. Config fixed. |
| `plot_wrtc_propagation_animation` | **ACTIVE** | PNG gen removed. Config fixed. Syntax verified. |
| `chart_qso_breakdown` | **ACTIVE** | PNG gen removed. |
| `plot_comparative_band_activity` | **ACTIVE** | PNG gen removed. |
| `plot_comparative_run_sp` | **ACTIVE** | PNG gen removed. |
| `plot_cumulative_difference` | **ACTIVE** | PNG gen removed. |
| `base_rate_report` | **ACTIVE** | PNG gen removed. |
| `chart_point_contribution` | **ACTIVE** | PNG gen removed. |