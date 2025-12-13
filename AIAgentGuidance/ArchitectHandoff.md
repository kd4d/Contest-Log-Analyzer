# Architect Handoff Notes

**Date:** 2025-12-13
**To:** Incoming Architect
**Focus:** Phase 4, Step 2 (Stabilization & Routing Fix)

## Context & Status
We are stabilizing the Web Dashboard. The critical "Dependency Poisoning" (Matplotlib crash) and "Missing Directory" (FileNotFoundError) issues have been **SOLVED**.
* **Guard & Triage:** `_report_utils.py` and `reports/__init__.py` now handle missing `matplotlib` dependencies gracefully. Logs show legacy reports are being skipped without crashing the container.
* **Scaffolding:** `report_generator.py` now systemically creates output directories (`os.makedirs`). Verification logs show reports successfully writing to disk.

## The Current Blocker: "The Animation 404"
The "Interactive Animation" report generates successfully but returns a **404 Not Found** in the browser.
* **Diagnosis:** **Path Mismatch / Semantic Error.**
* **Evidence:** The generator logs show it writing to `.../reports/.../html/`. The browser requests `.../reports/.../animations/`.
* **Root Cause:** The `plot_interactive_animation.py` plugin currently defines itself as `report_type = 'html'`. The generator routes this to a generic `html` folder, but the Dashboard expects it in the semantic `animations` folder.

## Strategic Decision: Deprecate the `html` Folder
We have decided to **remove the `html` output folder entirely**.
* **Reason:** `html` was a "Pathfinder" artifact for proof-of-concept. It represents a file extension, not a semantic function.
* **New Standard:** All reports must be routed based on their semantic function (`plot`, `text`, `animation`, `chart`), regardless of their file format.

## Immediate Priorities
The Incoming Architect must execute the **"Semantic Routing Fix"** defined in the attached `TechnicalDirective.md`.