# Architect Handoff: The JSON Pivot

**From:** Architect (Session 2.1)
**To:** Incoming Architect
**Date:** 2025-12-29

## The "Why" (Context Bridge)

We are in the middle of a critical architectural pivot for the Web Dashboard. The previous "Iframe-based" approach caused unresolvable layout issues (double scrollbars, clipping).

**The New Standard:**
We have established a **Component-Based Architecture**.
1.  **Python** generates pure data (`.json`) using the DAL.
2.  **Django/JS** fetches that data and renders it into a `<div>` using `Plotly.newPlot()`.

## Immediate Priorities (The Queue)

You are receiving the project in a **mixed state**. The `Strategy` tab of the QSO Dashboard is modernized (JSON), but the other tabs (`Rates`, `Points`) are still legacy (Iframes).

**Your Mission:** Complete **Phase 2 (The Rollout)**.
1.  **Target Reports:**
    * `plot_qso_rate.py` (Used in "QSOs by Band" tab and Global Context).
    * `plot_point_rate.py` (Used in "Points & Bands" tab).
    * `chart_point_contribution.py` (Used in "Points & Bands" tab).
2.  **Required Action:**
    * Update these generators to output `.json` artifacts (enforcing `.tolist()` for data arrays).
    * Update `views.py` to discover these JSON files.
    * Update `qso_dashboard.html` to render them via `renderChart()`.

## Critical Warnings (Do Not Ignore)

1.  **The "Straight Line" Bug:** When serializing data for JSON, you **MUST** convert Pandas Series to Lists (`series.tolist()`) before passing them to Plotly. Failing to do so causes the JSON serializer to dump the *Index* instead of the *Values*, resulting in a garbage straight-line plot.
2.  **Layout Authority:** Do **NOT** override chart margins in the Javascript/HTML. The Python backend (`PlotlyStyleManager`) calculates precise margins for titles and footers. Overriding them in the frontend causes clipping.
3.  **The Three-Artifact Rule:** For now, continue generating `.html` and `.png` files alongside the `.json`. The `.html` is required to keep the "Full Screen" buttons working until we refactor the viewer in Phase 3.