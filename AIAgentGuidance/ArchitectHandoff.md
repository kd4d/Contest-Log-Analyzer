# Architect Handoff Notes

**Date:** 2025-12-07
**To:** Incoming Architect
**Focus:** Phase 2 - Visualization Standardization (Tracer Bullet)

## Context
We have just completed a major hardening of the `AIAgentWorkflow.md` (v4.4.0). The system now enforces strict output sanitization automatically via the "Act as Builder" macro and requires explicit triggers for Handoffs and Overrides. We are now ready to resume the technical work of Phase 2.

## The Immediate Task: Plotly Migration (Tracer Bullet)
The next task is to convert `chart_point_contribution.py` from Matplotlib to Plotly.

### **Critical Requirement (Ephemeral Constraint)**
The Builder Plan **MUST** mandate that `chart_point_contribution.py` generates **two** output files for every run. This requirement exists only in this handoff, not yet in the code:
1.  **Static (`.png`):** Via `kaleido` (to preserve legacy CLI contract).
2.  **Interactive (`.html`):** Via `fig.write_html(include_plotlyjs='cdn')`. This is a proof-of-concept for the future Web UI.

## Decisions
1.  **Parallel Styles:** We are creating a new `PlotlyStyleManager` class. Do **NOT** modify the existing `MPLStyleManager`, as it is still used by legacy reports.
2.  **Standard Layout:** The new Style Manager must provide a `get_standard_layout(title)` method to enforce consistent margins and titles across all Plotly charts.

## Instructions for Next Session
1.  **Bootstrap:** Ingest the **Full Project Bundle** + this **Handoff** + the **Roadmap**.
2.  **Workflow Check:** Ensure you are using `AIAgentWorkflow.md` v4.4.0.
3.  **Planning:** Generate the **Builder Execution Kit** for the `chart_point_contribution` migration. Ensure the Plan explicitly includes the **HTML Bundle** requirement described above.
4.  **Execution:** When prompting the user, provide the simple trigger **"Act as Builder"**, as Protocol 1.6 now handles the formatting constraints automatically.