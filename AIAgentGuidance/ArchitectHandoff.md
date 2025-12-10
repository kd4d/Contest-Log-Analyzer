# Architect Handoff Notes

**Date:** 2025-12-10
**To:** Incoming Architect / Builder
**Focus:** Phase 2 - Visualization Standardization (Migration)

## Context
We are at the final visual report for Phase 2!

## The Immediate Task: `plot_comparative_run_sp.py`
This report visualizes the "Mode of Operation" (Run vs S&P) as a timeline for two logs.

### **Technical Requirements**
1.  **Visualization Engine:** Replace `matplotlib` with `plotly.graph_objects`.
2.  **Chart Type:** Discrete Heatmap (Gantt-style).
    * **Layout:** `make_subplots(rows=len(bands), cols=1, shared_xaxes=True)`.
    * **Margins:** `margin=dict(t=140)` (ADR-008).
3.  **Data Source:** `MatrixAggregator` (Already integrated).
    * Returns `activity_status` (List of Lists of Strings: 'Run', 'S&P', 'Mixed', 'Inactive').
4.  **Implementation Strategy (Discrete Heatmap):**
    * Map the status strings to Integers:
        * 'Inactive' -> `np.nan`
        * 'Run' -> 1
        * 'S&P' -> 2
        * 'Mixed' -> 3
    * **Color Scale:** Construct a custom `colorscale` to map these integers to `PlotlyStyleManager` colors:
        * 1: Green (`#2ca02c`)
        * 2: Blue (`#1f77b4`)
        * 3: Gray (`#7f7f7f`)
    * **Traces:** One `go.Heatmap` per Band.
        * `z`: 2D array `[ [Log2_Ints], [Log1_Ints] ]`.
        * `y`: `[Call2, Call1]` (Log 1 on top).
        * `x`: Time bins.
        * `xgap=0`, `ygap=2` (Small vertical gap between the two operator lanes).
5.  **Output:**
    * **Static:** `.png` (width=1600).
    * **Interactive:** `.html`.

### **Migration Notes**
* **Colors:** The legacy code used Red/Green/Yellow. **We are switching to Green/Blue/Gray** to match the application standard. This is a deliberate design change.
* **Pagination:** Preserve the logic that splits bands across pages (`_run_plot_for_slice`). Replace the plotting logic inside `_generate_plot_for_page`.

## Instructions for Next Session
1.  **Execution:** Convert `plot_comparative_run_sp.py`.
2.  **Completion:** This concludes Phase 2 visualization tasks.