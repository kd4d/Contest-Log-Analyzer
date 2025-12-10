# Implementation Plan - Phase 2: Comparative Run/S&P Timeline Migration

**Target:** `contest_tools/reports/plot_comparative_run_sp.py`
**Goal:** Migrate the visualization engine from Matplotlib to Plotly to create a "Discrete Heatmap" timeline of operating style (Run/S&P).

## 1. Builder Bootstrap Context
* **Target File:** `contest_tools/reports/plot_comparative_run_sp.py`
* **Style Authority:** `contest_tools/styles/plotly_style_manager.py`
* **Utility Support:** `contest_tools/reports/_report_utils.py`
* **Data Source:** `MatrixAggregator` (Already integrated).

## 2. Technical Specification

### 2.1. Visualization Engine Upgrade
* **Remove:** `matplotlib.pyplot`, `matplotlib.patches`, `matplotlib.dates`.
* **Add:** `plotly.graph_objects` as `go`, `plotly.subplots.make_subplots`.

### 2.2. Chart Logic (`_generate_plot_for_page`)
* **Pagination:** Preserve the `bands_on_page` iteration logic to split large band sets (e.g., 8 per page).
* **Layout:**
    * `rows=len(bands_on_page)`, `cols=1`.
    * `shared_xaxes=True`.
    * `vertical_spacing=0.03`.
    * `subplot_titles=[f"Band: {b}" for b in bands_on_page]`.
    * **Margin Override:** `margin=dict(t=140)` (ADR-008).
* **Implementation Strategy (Discrete Heatmap):**
    * **Data Transformation:**
        * Convert `activity_status` strings to integers:
            * 'Inactive' -> `np.nan` (Transparent).
            * 'Run' -> `1` (Green).
            * 'S&P' -> `2` (Blue).
            * 'Mixed' -> `3` (Gray).
    * **Structure:** Construct a 2D Z-matrix for each band:
        * `z = [[Log2_Ints], [Log1_Ints]]` (Log 1 is Row 0/Top, Log 2 is Row 1/Bottom).
    * **Trace:** `go.Heatmap`.
        * `z=z_matrix`.
        * `x=time_bins`.
        * `y=[call2, call1]` (Note order: Y-axis usually plots bottom-up, so index 0 is bottom. Verify: If Z-row 0 corresponds to Y-label 0, ensure Log 2 is at bottom).
        * `xgap=0` (Continuous time).
        * `ygap=2` (Gap between operator lanes).
        * `showscale=False` (Hide colorbar, use Legend instead).
    * **Color Scale:** Custom discrete scale mapping 1, 2, 3 to the `PlotlyStyleManager` hex codes.
        * Because Heatmaps interpolate, we must define a hard-edged scale or valid ranges.
        * **Simpler Approach:** Use `colorscale=[[0, 'white'], [0.25, 'white'], [0.25, 'green'], [0.5, 'green'], [0.5, 'blue'], [0.75, 'blue'], [0.75, 'gray'], [1.0, 'gray']]` mapping to normalized values 0.33, 0.66, 1.0.
        * **Robust Approach:** Normalize inputs to 0, 1, 2. Map 0->Green, 1->Blue, 2->Gray.
* **Legend:** Add dummy `go.Scatter` traces (mode='markers', opacity=0) to generate a legend for "Run", "S&P", "Mixed".

### 2.3. Styling & Layout
* **Title:** Standard 2-line title via `PlotlyStyleManager`.
* **Dimensions:** `width=1600`. Height dynamic based on bands.
* **Axes:**
    * Y-Axis: Callsign labels (`ticktext=[call2, call1]`, `tickvals=[0, 1]`).
    * X-Axis: Contest Time (UTC).

### 2.4. Output Generation
* **PNG:** `fig.write_image`.
* **HTML:** `fig.write_html`.

## 3. Step-by-Step Execution Instructions

1.  **Refactor Imports:**
    * Remove Matplotlib imports.
    * Import `plotly.graph_objects` and `make_subplots`.
    * Import `PlotlyStyleManager`.

2.  **Refactor `_generate_plot_for_page`:**
    * **Setup:** Initialize `make_subplots`.
    * **Data Loop:** Iterate `bands_on_page`.
        * Extract activity rows for Log 1 and Log 2.
        * Map strings to integers.
        * Create `go.Heatmap` trace.
        * Add to subplot.
    * **Legend:** Add dummy invisible traces to populate the legend with the correct colors.
    * **Layout:** Apply standard layout + margin override + dynamic height.
    * **Saving:** Implement `write_image` and `write_html`.

3.  **Cleanup:**
    * Ensure `create_output_directory` is called.
    * Remove the manual bar-drawing logic.

## 4. Safety Protocols
* **Color Consistency:** Ensure 'Run' maps to Green (`#2ca02c`) and 'S&P' maps to Blue (`#1f77b4`) to match other reports.
* **Orientation:** Verify that Log 1 is consistently the "Top" lane in the visualization.

## 5. Technical Debt Register
* **Observation:** The integer mapping logic is local to this file but relies on the string constants from `MatrixAggregator`.