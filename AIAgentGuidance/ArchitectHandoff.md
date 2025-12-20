# Architect Handoff Notes

**Date:** 2025-12-20
**From:** Outgoing Architect
**To:** Incoming Architect

---

## 1. The "Hot" Context (Read This First)
**We are currently in a broken state.**
A recent refactoring to standardize chart titles (Phase 1.5) accidentally removed a variable (`is_single_band`) that was still required for filename generation.
* **Symptom:** `plot_qso_rate.py` and 3 other reports crash with `NameError`.
* **Result:** No files are generated. The Web Dashboard returns **404 Not Found** because it links to files that don't exist.

## 2. Immediate Action Items
Your **first** action must be to execute the **Hotfix** defined in the previous session (or re-generate it).

1.  **Apply Hotfix:**
    * Update `contest_tools/reports/_report_utils.py` to add `build_filename()`.
    * Patch `plot_qso_rate.py`, `plot_point_rate.py`, `plot_cumulative_difference.py`, and `plot_comparative_band_activity.py`.
    * *Why:* This fixes the crash and ensures files land on disk with consistent names.

2.  **Verify & Proceed to Phase 2 (Manifest):**
    * Once the crash is fixed, you must implement the **Session Manifest**.
    * The Dashboard's current logic ("guessing" filenames based on inputs) is flawed. If 1 of 3 logs is bad, the generator correctly filters it out (2 logs), but the View looks for a 3-log filename -> 404.
    * **Solution:** The Generator must produce a `manifest.json` of *created* files. The View must read this manifest.

## 3. "Watch Out" For...
* **Strict Naming:** We are moving toward strict, centralized naming (`_report_utils.build_filename`). Do not allow ad-hoc string formatting in individual reports.
* **Partial Failures:** The system must handle "2 Good Logs + 1 Bad Log" gracefully. Do not re-introduce `if any(log.empty): return`. The generator must filter valid logs and proceed.
* **Matplotlib:** We are actively purging Matplotlib. Do not accept new code using it. Push for Plotly.

## 4. Current File State
The `project_bundle.txt` you will receive contains the **Regressed Code** (Phase 1.5 Partial). It does **NOT** contain the Hotfix. You must apply the fix immediately upon resumption.