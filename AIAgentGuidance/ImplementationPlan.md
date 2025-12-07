# Implementation Plan - Phase 2: Visualization Standardization (Tracer Bullet)

**Version:** 2.0.0
**Date:** 2025-12-07

## 1. Builder Bootstrap Context
* **Goal:** Migrate the visualization engine for `chart_point_contribution.py` from Matplotlib to Plotly.
* **Deliverables:**
    1.  **Static Output:** A `.png` file (via `kaleido`) to satisfy legacy CLI contracts.
    2.  **Interactive Output:** A `.html` file (via `fig.write_html`) as a Phase 3 Proof-of-Concept.
* **Standards:**
    * **Style Guide:** `Docs/CLAReportsStyleGuide.md` (Section 5.2 - Interactive Plots).
    * **Styling:** Must use a new `PlotlyStyleManager` class to ensure "Brand Consistency" (colors, layouts) without relying on Matplotlib dependencies.
* **Data Source:** `CategoricalAggregator` (Existing DAL).

## 2. Safety Protocols
* **Visual Parity:** The new Plotly chart must visually match the legacy Matplotlib charts (Pie charts for each log) as closely as possible.
* **File Contract:** The report MUST still output a `.png` file to the `charts/` directory. The `.html` file is an *additive* feature.
* **Parallel Co-existence:** Do **NOT** modify or remove `MPLStyleManager`. It is required for the 10+ other reports that have not yet been converted.
* **No Aggregator Changes:** Do not modify the `CategoricalAggregator`. We are only changing the Presentation Layer.

## 3. Technical Debt Register (Observer)
* **Observation:** `MPLStyleManager` is tightly coupled to Matplotlib. We are creating a parallel `PlotlyStyleManager`. In Phase 4, these should be consolidated into a generic `StyleConfig` dictionary.

## 4. Execution Steps

### Step 1: Create `contest_tools/styles/plotly_style_manager.py`
* **Action:** Create a new class `PlotlyStyleManager`.
* **Logic:**
    * Port the color palette from `MPLStyleManager` to pure Python lists/dictionaries (removing `matplotlib` imports).
    * Implement `get_point_color_map(point_values)` (Business Logic parity).
    * Implement `get_qso_mode_colors()` (Business Logic parity).
    * **NEW:** Implement `get_standard_layout(title)` to return a standard `go.Layout` dictionary (fonts, margins, template) compliant with the Style Guide.

### Step 2: Refactor `contest_tools/reports/chart_point_contribution.py`
* **Action:** Rewrite the `Report` class to use Plotly.
* **Changes:**
    * **Imports:** Remove `matplotlib`, `gridspec`. Add `plotly.graph_objects`, `plotly.subplots`. Import `PlotlyStyleManager`.
    * **Method `_create_plot_for_log`:**
        * Replace `ax.pie` with `go.Pie`.
        * Use `PlotlyStyleManager.get_point_color_map` for consistent coloring.
    * **Method `generate`:**
        * Replace `plt.figure` / `GridSpec` with `plotly.subplots.make_subplots`.
        * Define rows/cols logic similar to the existing math.
        * Apply `PlotlyStyleManager.get_standard_layout`.
        * **Save Operation 1 (Static):** Use `fig.write_image` to save the PNG.
        * **Save Operation 2 (Interactive):** Use `fig.write_html(..., include_plotlyjs='cdn')` to save the HTML bundle.
    * **Verification:** Ensure `create_output_directory` is called before saving.

## 5. Verification
* **Command:** `python run_regression_test.py`
* **Expected Result:** The test should run without errors. The `charts/` directory should contain both `.png` and `.html` versions of the point contribution chart.