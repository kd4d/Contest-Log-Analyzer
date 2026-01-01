# Architect Handoff: Context Bridge

**From:** Architect (Session A - Legacy)
**To:** Architect (Session A - Successor)
**Date:** 2025-12-30

## 1. The Strategic Context
We are mid-transition in two major areas:
1.  **Workflow Architecture:** We just deployed **Workflow v5.0.1**, which enforces a strict "V-Model" (Session A for Analysis, Session B for Building). *Do not deviate from this.* The "Anti-Simulation" clause (Protocol 4.4) is a hotfix to prevent the Builder from auto-completing tasks.
2.  **Visual Language:** We have established "Concept 7" (The Integrated Data Grid) as the new standard for the Multiplier Dashboard. This replaces simple tables with hybrid Bar/Number rows.

## 2. Recent Decisions (The "Why")
* **Run/S&P Logic:** We mapped "Both" (worked on both Run and S&P) to "Run" in `multiplier_stats.py`. *Rationale:* If you can hold a frequency (Run), that is the dominant skill/mode we want to track, even if you also picked it up S&P.
* **Text Report Verbosity:** We explicitly widened the text report columns to ~37 chars to support `[Run:60 S&P:25 Unk:5]`. *Rationale:* "Auditability" is paramount. The dashboard visuals must be verifiable against a text file.
* **CSS Inline Styles:** The `multiplier_dashboard.html` currently contains inline CSS classes (`.bar-track`, `.bg-run`, etc.). *Rationale:* Rapid prototyping of Concept 7. This is recognized technical debt.

## 3. Immediate Technical Debt (The "Incomplete Transition")
The User has flagged an "incomplete transition to the new HTML report architecture." Here is the breakdown:

### A. The CSS Fragmentation
* **Current State:** New dashboard styles exist in `<style>` blocks within `multiplier_dashboard.html`.
* **Target State:** These must be extracted to the global `static/css/styles.css` (or `base.css`) to ensure reusability across other reports.
* **Risk:** If we create a second dashboard (e.g., "Rate Analysis"), we will duplicate these styles, creating maintenance drift.

### B. The Legacy Report Gap
* **Current State:** `multiplier_dashboard.html` uses the new "Card/Grid" layout. Older reports (e.g., `view_report.html` wrappers) might still use legacy Bootstrap tables.
* **Target State:** Audit all "Summary" cards in the system. They should all eventually adopt the "Integrated Data Grid" pattern where applicable.

### C. The "Unique" Metric Scope
* **Current State:** We calculate `unique_run` and `unique_sp` *only* in `multiplier_stats.py`.
* **Gap:** Other aggregators (e.g., `rate_stats.py`, `zone_stats.py`) do not yet expose this "Mode of Acquisition" breakdown.
* **Action:** Evaluate if the `_get_run_sp_status` logic should be moved to a central utility mixin (e.g., in `ComparativeEngine`) so all reports can use it.

## 4. Priority Tasks for Next Session
1.  **Refactor CSS:** Extract the Concept 7 styles from `multiplier_dashboard.html`.
2.  **Audit `base.html`:** Ensure the new layout grid doesn't break mobile responsiveness on smaller screens (the 3-column layout is dense).
3.  **Verify Workflow:** Run a "Protocol Onboarding" drill (Protocol 1.8) to confirm you understand the new v5.0.1 rules (specifically the Session A/B split).