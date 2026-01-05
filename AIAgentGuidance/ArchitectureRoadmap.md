__CODE_BLOCK__
# Architecture Roadmap: Contest Log Analytics

**Version:** 2026.01.05-Beta
**Status:** Phase 3 Execution

## Phase 3: The Web Pathfinder (Current)
**Goal:** Transition from a local CLI tool to a stateless, containerized Web Dashboard.
**Core Constraint:** The web container (`web-1`) is lightweight. It lacks `matplotlib`, `kaleido`, and `ffmpeg`.

### 1. Visualization Architecture (Active Sprint)
* [x] **Adopt Plotly:** All new charts must use `plotly` for HTML/JS rendering.
* [x] **Deprecate Backend PNGs:** Removed `fig.write_image()` calls from all core reports.
* [ ] **Client-Side Capture:** Rely on Plotly's native "Download as PNG" (Modebar) or `html2canvas` for static exports.

### 2. The Data Abstraction Layer (DAL)
* [x] **Decoupling:** Reports must not calculate data. They must request data from `data_aggregators`.
* [x] **WORM Strategy:** Expensive calculations (Matrix, Breakdown) are run once during ingestion (`analyze_logs`) and serialized to JSON artifacts (`json_multiplier_breakdown`).
* [x] **Hydration:** The Dashboard hydrates views from these JSON artifacts, bypassing `LogManager` parsing on page load.

### 3. Report Modernization Status
| Report ID | Status | Action Required |
| :--- | :--- | :--- |
| `chart_comparative_activity_butterfly` | **ACTIVE** | Logic restored. PNG generation removed. |
| `plot_wrtc_propagation` | **ACTIVE** | Converted to Plotly. PNG generation removed. |
| `plot_wrtc_propagation_animation` | **Pending** | Converted to HTML Animation, pending deployment. Remove PNG generation. |
| `chart_qso_breakdown` | **Legacy** | Remove `fig.write_image()` call. |
| `plot_comparative_band_activity` | **Legacy** | Remove `fig.write_image()` call. |
| `plot_comparative_run_sp` | **Legacy** | Remove `fig.write_image()` call. |
| `plot_cumulative_difference` | **Legacy** | Remove `fig.write_image()` call. |
| `base_rate_report` | **Legacy** | Remove `fig.write_image()` call. |
__CODE_BLOCK__