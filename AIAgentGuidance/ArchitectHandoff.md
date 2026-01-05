--- FILE: ArchitectHandoff.md ---
# Architect Handoff: Context Bridge

**From:** Session A (Analyst/Architect)
**To:** Session B (Architect/Builder)
**Date:** 2026-01-05

## 1. The Strategic Context
We are in **Phase 3: The Web Pathfinder**. The primary objective is **Data Abstraction Layer (DAL) Decoupling**. To enable the Web Dashboard's "Fast Path" (JSON hydration), all reports must stop accessing `ContestLog` DataFrames directly. They must instead request "Pure Python Primitives" (dictionaries/lists) from the `data_aggregators` package.

## 2. Recent Accomplishments
* **Web Stabilization:** Successfully removed `kaleido` and `matplotlib` dependencies from all visual reports (`base_rate_report`, `chart_point_contribution`, `plot_comparative_band_activity`, etc.).
* **Text Report Decoupling (Successes):**
    * `text_summary.py`: Refactored to use `CategoricalAggregator.get_log_summary_stats`.
    * `text_continent_summary.py`: Refactored to use `CategoricalAggregator.get_continent_stats`.

## 3. The Failure Point (Immediate Priority)
We attempted to decouple **`text_qso_comparison.py`**.
* **Status:** **FAILED**.
* **Incident:** The Builder hallucinated during file generation and overwrote the `categorical_stats.py` aggregator file with the report source code.
* **Recovery:** The user rejected the bundle. **The codebase currently has `text_qso_comparison.py` in its legacy (coupled) state.**
* **Next Action:** You must restart the decoupling process for `text_qso_comparison.py`. The Implementation Plan logic was sound (enhance `compute_comparison_breakdown` to support `include_dupes` and return `common_detail`), but the execution failed.

## 4. Pending Priorities
1.  **Retry `text_qso_comparison.py`:**
    * Target: `contest_tools/reports/text_qso_comparison.py`
    * Dependency: `contest_tools/data_aggregators/categorical_stats.py` (needs enhancement).
2.  **`text_score_report.py`:** This is the most complex report. It requires migrating hierarchical scoring logic and `sum_by_band` vs `once_per_log` handling into the DAL.
3.  **`text_comparative_score_report.py`:** Will likely share the aggregator logic derived for `text_score_report.py`.
4.  **Rate Sheets:** Review `text_rate_sheet.py` to ensure it consumes `TimeSeriesAggregator` output without accessing the raw DF.

## 5. Technical Constraints
* **Inert Material:** Do not fix bugs in the reports unless they block decoupling.
* **Output Fidelity:** The text output of the new reports must match the legacy reports byte-for-byte (excluding timestamp headers) to pass regression tests.
* **DAL Purity:** Aggregators must return JSON-serializable types. No Pandas Series/DataFrames.

--- FILE: ArchitectureRoadmap.md ---
**Version:** 2026.01.05-Beta-4
**Status:** Phase 3 Execution

## Phase 3: The Web Pathfinder (Current)
**Goal:** Transition from a local CLI tool to a stateless, containerized Web Dashboard.
**Core Constraint:** The web container (`web-1`) is lightweight. It lacks `matplotlib`, `kaleido`, and `ffmpeg`.

### 1. Visualization Architecture (Stabilization Complete)
* [x] **Adopt Plotly:** All new charts must use `plotly` for HTML/JS rendering.
* [x] **Deprecate Backend PNGs:** Removed `fig.write_image()` calls from all core and legacy reports.
* [x] **Client-Side Capture:** Configured `toImageButtonOptions` to ensure clean filenames for client-side downloads.

### 2. The Data Abstraction Layer (DAL)
* [ ] **Decoupling (Text Reports):**
    * [x] `text_summary.py`
    * [x] `text_continent_summary.py`
    * [ ] `text_qso_comparison.py` (Pending - Previous Attempt Failed)
    * [ ] `text_score_report.py` (Pending)
    * [ ] `text_comparative_score_report.py` (Pending)
    * [ ] `text_rate_sheet.py` (Verify)
* [x] **WORM Strategy:** Expensive calculations (Matrix, Breakdown) are run once during ingestion (`analyze_logs`) and serialized to JSON artifacts (`json_multiplier_breakdown`).
* [x] **Hydration:** The Dashboard hydrates views from these JSON artifacts, bypassing `LogManager` parsing on page load.

### 3. Report Modernization Status
| Report ID | Status | Action Required |
| :--- | :--- | :--- |
| `text_summary` | **DECOUPLED** | None. |
| `text_continent_summary` | **DECOUPLED** | None. |
| `text_qso_comparison` | **COUPLED** | **PRIORITY 1**: Retry DAL migration. |
| `text_score_report` | **COUPLED** | Needs DAL migration. |
| `text_comparative_score_report` | **COUPLED** | Needs DAL migration. |
| `chart_comparative_activity_butterfly` | **ACTIVE** | Logic verified. |
| `plot_wrtc_propagation` | **ACTIVE** | PNG gen removed. |