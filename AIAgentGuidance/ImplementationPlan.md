# Implementation Plan - Phase 2: Visualization Standardization (chart_qso_breakdown)

**Goal:** Migrate `contest_tools/reports/chart_qso_breakdown.py` from Matplotlib to Plotly to support interactive web reports while maintaining legacy static image generation.

## 1. Builder Bootstrap Context
* **Target File:** `contest_tools/reports/chart_qso_breakdown.py`
* **Reference Files:**
    * `contest_tools/styles/plotly_style_manager.py` (Style Authority)
    * `contest_tools/data_aggregators/categorical_stats.py` (Data Source)
    * `contest_tools/reports/_report_utils.py` (Utils)

## 2. Technical Design & Constraints

### 2.1. Visualization Engine
* **Library:** `plotly.graph_objects` (via `go.Figure`, `go.Bar`) and `plotly.subplots`.
* **Chart Type:** Stacked Bar Chart.
    * **X-Axis:** Categories (Unique Log1, Common, Unique Log2).
    * **Y-Axis:** QSO Counts.
    * **Stacks:** Run, S&P, Mixed/Unk.
* **Subplots:** One subplot per Band (plus 'All Bands' if applicable, though the current logic iterates bands). Use dynamic row/col calculation based on band count.

### 2.2. Styling (Mandatory)
* **Colors:** MUST use `PlotlyStyleManager.get_qso_mode_colors()` to ensure consistency:
    * Run: Green
    * S&P: Blue
    * Mixed/Unk: Gray
* **Layout:** MUST use `PlotlyStyleManager.get_standard_layout(title)` as the base configuration.
* **Annotations:** Subplot titles must be generated dynamically.

### 2.3. Data Source
* **Aggregator:** Continue using `self.aggregator.compute_comparison_breakdown`.
* **Logic:** The existing `_prepare_data` method returns a dictionary `{'data': {'Run': [...], 'S&P': [...]}}`. This structure maps directly to Plotly traces.

### 2.4. Output Standards (Dual Output)
* **Static:** Save as `.png` using `fig.write_image()`.
* **Interactive:** Save as `.html` using `fig.write_html(include_plotlyjs='cdn')`.
* **Directory:** Ensure the output directory exists using `create_output_directory`.

## 3. Execution Steps

### Step 1: Update Imports
* Remove `matplotlib.pyplot`.
* Add `plotly.graph_objects` as `go`.
* Add `plotly.subplots.make_subplots`.
* Import `PlotlyStyleManager` from `contest_tools.styles.plotly_style_manager`.

### Step 2: Refactor `generate` Method
* Calculate grid dimensions (rows/cols) based on the number of bands.
* Initialize `fig` using `make_subplots` with `subplot_titles`.
* Iterate through bands:
    1.  Call `self._prepare_data(band)`.
    2.  Iterate through modes (`Run`, `S&P`, `Mixed/Unk`).
    3.  Add a `go.Bar` trace for each mode to the specific subplot.
        * **Crucial:** Set `showlegend=True` only for the first subplot to avoid duplicate legend entries.
* Update Layout:
    * Set `barmode='stack'`.
    * Apply `PlotlyStyleManager.get_standard_layout()`.
    * Set dynamic height based on row count (`400 * rows`).

### Step 3: Implement Dual Save
* Save `filename.png`.
* Save `filename.html`.
* Return list of saved paths.

## 4. Safety Protocols
* **Zero-Inference:** Do not guess color codes; use the Style Manager.
* **Preservation:** Do not modify the Aggregator logic.
* **Verification:** Verify the file saves to the correct path.

## 5. Technical Debt Register
* *Observation:* The `MatrixAggregator` (used in other reports) uses raw lists while `CategoricalAggregator` uses Dictionaries. Future refactoring should standardize DAL return types, but this is out of scope for this migration.