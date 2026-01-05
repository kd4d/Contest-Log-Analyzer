# Architect Handoff: Context Bridge

**From:** Session A (Analyst/Architect)
**To:** Session B (Architect/Builder)
**Date:** 2026-01-04

## 1. The Strategic Context
We are mid-flight in **Phase 3 (Web Architecture)**. The immediate priority is resolving the "Missing Dependency" errors caused by `matplotlib` and `kaleido` calls in the web container.

## 2. Critical Incident: The "Butterfly" Overwrite
* **Incident:** In a previous session, the Builder accidentally overwrote `chart_comparative_activity_butterfly.py` with the source code for `plot_wrtc_propagation.py`.
* **Status:** The file on disk is currently corrupt (wrong logic, wrong report ID).
* **Fix:** A specific implementation plan exists to restore the correct MatrixAggregator-based logic. This must be applied immediately.

## 3. Immediate Priorities (The "To-Do" List)
1.  **Fix `chart_comparative_activity_butterfly.py`:** Restore correct logic and ensure it uses Plotly.
2.  **Deprecate PNG Generation:** Systematically strip `fig.write_image()` calls from *all* reports. This will stop the "Kaleido missing" errors and speed up processing.
3.  **Deploy WRTC Reports:** Apply the already-approved Plotly conversion for `wrtc_propagation` and its animation.

## 4. Technical Constraints for Session B
* **No Matplotlib:** Do not import `matplotlib.pyplot`. Use `plotly.graph_objects`.
* **No Kaleido:** Do not call `write_image`. Generate `.html` and `.json` only.
* **No FFmpeg:** Animations must be HTML/JS (Plotly Frames), not MP4 video.

## 5. Next Steps
Review the `project_bundle.txt`. You will see the "Corrupt" Butterfly chart. Your first move is to generate a **Builder Execution Kit** that:
1.  Restores the Butterfly Chart (Clean Code).
2.  Updates `base_rate_report.py` and others to stop saving PNGs.