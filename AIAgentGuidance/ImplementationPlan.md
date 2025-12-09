# Implementation Plan - Phase 2: Visualization Standardization (Batch 2)

**Version:** 1.0.0
**Date:** 2025-12-08
**Target:** `chart_point_contribution_single.py`

## 1\. Builder Bootstrap Context

The Builder requires the following files to execute this plan:

  * `contest_tools/reports/chart_point_contribution_single.py` (Target)
  * `contest_tools/styles/plotly_style_manager.py` (Style Dependency)
  * `contest_tools/data_aggregators/categorical_stats.py` (Data Dependency)
  * `contest_tools/reports/_report_utils.py` (Utility Dependency)

## 2\. Technical Debt Register

  * **Report Returns:** The `generate` method signature for reports typically returns a `str` (message) or `List[str]` (files). We must ensure consistent return types across the unified engine in Phase 3. For now, we return `List[str]` containing both the PNG and HTML paths.

## 3\. Safety Protocols

  * **Visual Parity:** The new Plotly charts must maintain the same "Drill-Down" logic (One pie per band) as the Matplotlib version.
  * **Output Dual-Stack:** The report **MUST** output both a static `.png` (for legacy CLI compatibility) and an interactive `.html` (for future Web UI).
  * **Zero Logic Duplication:** Do not calculate stats inside the report. Use `CategoricalAggregator`.

## 4\. Execution Steps

### Task 1: Migrate `chart_point_contribution_single.py` to Plotly

  * **Goal:** Replace the Matplotlib engine with Plotly Graph Objects while maintaining the exact data flow.
  * **Imports:**
      * Remove: `matplotlib.pyplot`, `matplotlib.gridspec`.
      * Add: `plotly.graph_objects` as `go`, `plotly.subplots` (`make_subplots`).
      * Add: `contest_tools.styles.plotly_style_manager` import `PlotlyStyleManager`.
  * **Method Refactor: `generate(self, output_path, **kwargs)`**
    1.  **Data Fetching:**
          * Keep existing `get_valid_dataframe` logic to identify active bands.
          * Call `self.aggregator.get_points_breakdown(self.logs, band_filter=band)` inside the band loop.
    2.  **Layout Logic:**
          * Calculate `rows` and `cols` using the existing logic (Max 4 cols).
          * Initialize `fig = make_subplots(...)` with `specs=[[{'type': 'domain'}, ...]]` for Pie charts.
          * Generate subplot titles dynamically (e.g., `"{band} Band Points (Total: {N})"`).
    3.  **Trace Generation:**
          * Iterate through bands.
          * Extract breakdown data.
          * Generate consistent colors using `PlotlyStyleManager.get_point_color_map` (ensure global consistency across all pies).
          * Create `go.Pie` traces.
          * Add traces to specific grid cells (`row=..., col=...`).
    4.  **Styling:**
          * Apply `PlotlyStyleManager.get_standard_layout(title)`.
    5.  **Output:**
          * Construct filenames: `..._single.png` and `..._single.html`.
          * Save PNG via `fig.write_image`.
          * Save HTML via `fig.write_html`.
          * Return list of *both* file paths.

-----

# Manifest

```text
contest_tools/reports/chart_point_contribution_single.py
contest_tools/styles/plotly_style_manager.py
contest_tools/data_aggregators/categorical_stats.py
contest_tools/reports/_report_utils.py
```

-----

### **Next Steps**

1.  Create `builder_bundle.txt` containing the files listed in the Manifest.
2.  Upload `builder_bundle.txt`.
3.  To proceed, please provide the exact prompt: **"Act as Builder"**.