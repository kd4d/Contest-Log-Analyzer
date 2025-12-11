# Architect Handoff Notes

**Date:** 2025-12-11
**To:** Incoming Architect / Builder
**Focus:** Phase 2.5 (Animation Modernization)

## Context
We have codified the "Golden Path" workflow in Roadmap v2.0.2 (Three-Slot, Stateless, Source-Agnostic).
We are now clearing the final technical debt (Matplotlib/FFmpeg) before starting the Web Infrastructure build.

## The Immediate Task: Phase 2.5
We must convert the Animation report to Plotly. This allows us to build a lean Docker container in Phase 3 without complex video libraries.

## Instructions for Next Session
1.  **Execute:** Generate the Builder Execution Kit for Phase 2.5 (Animation).
2.  **Verify:** Ensure `run_regression_test.py` is updated to handle `.html` comparison for animations.