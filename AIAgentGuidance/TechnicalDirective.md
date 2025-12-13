# Technical Directive: Semantic Routing & Cleanup

**Target Audience:** Incoming Architect / Developer
**Priority:** Immediate
**Context:** Phase 4, Step 2 (Stabilization)

## Problem Statement
The "Interactive Animation" report fails to load (404) because it is stored in the wrong directory. It currently identifies as `report_type = 'html'`, causing it to be routed to a generic `html/` folder. The Web Dashboard expects it to reside in `animations/`.

## Strategic Directive
**Deprecate the `html` directory.** We are moving away from extension-based routing. All reports must be routed to semantic directories (`text`, `plots`, `charts`, `animations`).

## Execution Steps

### 1. Reclassify `plot_interactive_animation.py`
**Goal:** Force the animation report into the correct semantic bucket.
* **Action:** Edit `contest_tools/reports/plot_interactive_animation.py`.
* **Change:** Update the class attribute `report_type` from `'html'` to `'animation'`.

### 2. Refactor `report_generator.py`
**Goal:** Enforce semantic routing and remove the `html` bucket.
* **Action:**
    1.  Remove `self.html_output_dir` from the `__init__` method.
    2.  Remove the `elif report_type == 'html':` routing logic in the `run_reports` loop.
    3.  **Cleanup:** While in this file, remove the temporary "DEBUG TRACE" logging injected during the previous session. (The logs have served their purpose; restore the file to a clean state).

### 3. Verify
* **Action:** Restart the container and run the analysis.
* **Success Criteria:**
    1.  The `html/` folder is no longer created in the session directory.
    2.  The `interactive_animation` HTML file appears inside the `animations/` folder.
    3.  The Web Dashboard link opens the animation successfully (200 OK).