# Architect Handoff Notes

**Date:** 2025-12-08
**To:** Incoming Architect / Builder
**Focus:** Phase 2 - Visualization Standardization (Migration)

## Context
The Tracer Bullet (Phase 2 initial test) was successful. `chart_point_contribution.py` and its single-log counterpart have been fully migrated to Plotly, implementing the "Dual Output" standard (PNG + HTML) and utilizing the `PlotlyStyleManager`.

We are now proceeding with the general rollout of this standard to the remaining reports.

## The Immediate Task: `chart_qso_breakdown.py`
The next report to migrate is `chart_qso_breakdown.py`. This is a stacked bar chart comparing two logs.

### **Technical Requirements**
1.  **Visualization Engine:** Replace `matplotlib` with `plotly.graph_objects`.
2.  **Chart Type:** Use `go.Bar`.
    * **Mode:** `barmode='stack'`.
    * **Layout:** The chart must support multiple subplots (one per band), similar to the Matplotlib version. Use `plotly.subplots.make_subplots`.
3.  **Data Source:** Continue using `CategoricalAggregator.compute_comparison_breakdown`.
    * Iterate through the dictionary keys (`Run`, `S&P`, `Mixed/Unk`) to create traces.
4.  **Styling:**
    * Use `PlotlyStyleManager.get_qso_mode_colors()` to ensure the colors (Green/Blue/Gray) match the text reports and previous charts.
    * Use `PlotlyStyleManager.get_standard_layout()` for title and margins.
5.  **Output:**
    * **Static:** `.png` (via `fig.write_image`).
    * **Interactive:** `.html` (via `fig.write_html`, `include_plotlyjs='cdn'`).

## Decisions
* **Dual Output Mandate:** Every converted chart MUST output both formats to support the legacy CLI contract and the future Web UI.
* **Style Consistency:** Do not hardcode colors. Always fetch from `PlotlyStyleManager`.

## Instructions for Next Session
1.  **Bootstrap:** Ingest the **Full Project Bundle**.
2.  **Verification:** Confirm `chart_qso_breakdown.py` is the target in `ImplementationPlan.md`.
3.  **Execution:** Generate the **Builder Execution Kit** for this migration.