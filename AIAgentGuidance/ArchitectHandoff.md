# Architect Handoff Notes

**Date:** 2025-12-11
**To:** Incoming Architect / Builder
**Focus:** Phase 2.5 (Animation Modernization)

## Context
We have finalized the Roadmap (v2.0.3).
* **Strategy:** Stateless, Three-Slot UI.
* **Next Phase (Phase 3):** Building the Web MVP using CQ WW as the "Pathfinder" test case.
* **Current Block:** We must finish **Phase 2.5** to remove `ffmpeg` dependencies before we start Dockerizing in Phase 3.

## The Immediate Task: Phase 2.5
We must convert the Animation report to Plotly. This allows us to build a lean Docker container in Phase 3 without complex video libraries.

## Instructions for Next Session
1.  **Execute:** Generate the Builder Execution Kit for Phase 2.5 (Animation).
2.  **Verify:** Ensure `run_regression_test.py` is updated to handle `.html` comparison for animations.