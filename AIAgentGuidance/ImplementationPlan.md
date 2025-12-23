# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.140.0-Beta

## 1. File Identification
* `Docs/ReportInterpretationGuide.md` (Baseline: 0.119.1-Beta)
* `Docs/UsersGuide.md` (Baseline: 1.1.0)
* `README.md` (Baseline: 1.2.0)
* `Docs/ProgrammersGuide.md` (Baseline: 0.126.0-Beta)
* `web_app/analyzer/templates/analyzer/help_reports.html` (Baseline: Source 1708)

## 2. Surgical Changes

### 2.1. `Docs/ReportInterpretationGuide.md`
* **Update Header:** Bump version to `0.140.0-Beta` and date to today.
* **Add Section:** Insert "Multiplier Breakdown (Group Par)" under "2. Text Reports".
    * **Content:** Explain the concept of "Group Par" (Universe Count), "Common" (Intersection), and "Delta" (Distance from Par). Explain that this report highlights *relative* performance against the group's collective potential.
* **Update Section 6 (WRTC):** Ensure description matches the new interactive animation capabilities if needed (currently looks accurate in baseline).

### 2.2. `Docs/UsersGuide.md`
* **Update Header:** Bump version to `1.2.0` and date to today.
* **Update Section 5 (Available Reports):**
    * Add `html_multiplier_breakdown`: Multiplier Breakdown (HTML).
    * Add `text_multiplier_breakdown`: Multiplier Breakdown (Text).
    * Add `json_multiplier_breakdown`: JSON Multiplier Breakdown Artifact.

### 2.3. `README.md`
* **Update Header:** Bump version to `1.3.0` and date to today.
* **Update "Available Reports":**
    * Add `html_multiplier_breakdown`.
    * Add `text_multiplier_breakdown`.
    * Add `json_multiplier_breakdown`.

### 2.4. `Docs/ProgrammersGuide.md`
* **Update Header:** Bump version to `0.127.0-Beta` and date to today.
* **Add Section:** "The Manifest & WORM Strategy" under "Phase 3: Web Architecture".
    * **Content:** Document the use of `ManifestManager` for artifact discovery. Document the "Write Once, Read Many" (WORM) pattern where expensive aggregations are serialized to JSON artifacts (`json_multiplier_breakdown`) for instant dashboard hydration.

### 2.5. `web_app/analyzer/templates/analyzer/help_reports.html`
* **Locate:** The "Text Reports (Deep Dive)" card.
* **Insert:** A new entry for "Multiplier Breakdown" below "Missed Multipliers".
    * **Content:** "The 'Group Par' analysis. Compares your multiplier total against the 'Universe' of multipliers worked by the entire group. A negative Delta indicates multipliers you missed that others found."

## 3. Surgical Change Verification (`diff`)

--- BEGIN DIFF ---
--- Docs/ReportInterpretationGuide.md
+++ Docs/ReportInterpretationGuide.md
@@ -2,5 +2,5 @@
 
-**Version: 0.119.1-Beta**
-**Date: 2025-12-15**
+**Version: 0.140.0-Beta**
+**Date: 2025-12-23**
 
@@ -107,4 +107,14 @@
 
+### Multiplier Breakdown (`text_multiplier_breakdown` & `html_multiplier_breakdown`)
+This report provides a hierarchical "Group Par" analysis. It establishes a "Universe" of all unique multipliers worked by the entire group (e.g., all 3 logs combined) and compares each station against that standard.
+
+#### How to Interpret This Report
+* **Total Worked (Par):** The count of unique multipliers found by the group combined. This represents the "potential" score available on the band.
+* **Common:** The count of multipliers worked by *everyone* in the group.
+* **Delta:** The most critical metric. It shows your distance from the Group Par. A delta of `-10` means there were 10 multipliers worked by others that you missed.
+* **Strategic Insight:** In a team contest (like WRTC or Multi-Op), minimizing the standard deviation of the Delta across stations is key to maximizing the group score.
+
+---
+
 ### Multiplier Summary (`multiplier_summary`)
 This report lists every unique multiplier (e.g., each individual Country, Zone, or State) worked by one or more logs and shows the QSO count for that multiplier on each band.
--- Docs/UsersGuide.md
+++ Docs/UsersGuide.md
@@ -2,5 +2,5 @@
 
-**Version: 1.1.0**
-**Date: 2025-12-15**
+**Version: 1.2.0**
+**Date: 2025-12-23**
 
@@ -112,6 +112,7 @@
 #### **HTML Reports (`html/`)**
+* `html_multiplier_breakdown`: Multiplier Breakdown Report (Group Par)
 * `html_qso_comparison`: HTML QSO Comparison Report
 
@@ -129,4 +130,5 @@
 #### **Text Reports (`text/`)**
 * `comparative_continent_summary`: Comparative Continent QSO Summary
+* `text_multiplier_breakdown`: Multiplier Breakdown (Group Par)
 * `rate_sheet_comparison`: Comparative Rate Sheet
 * `comparative_score_report`: Comparative Score Report
@@ -135,4 +137,5 @@
 * `missed_multipliers`: Missed Multipliers
 * `multiplier_summary`: Multiplier Summary
+* `json_multiplier_breakdown`: JSON Multiplier Breakdown Artifact (Data Source)
 * `qso_comparison`: QSO Comparison Summary
 * `rate_sheet`: Hourly Rate Sheet 
--- README.md
+++ README.md
@@ -2,5 +2,5 @@
 
-**Version: 1.2.0**
-**Date: 2025-12-18**
+**Version: 1.3.0**
+**Date: 2025-12-23**
 
@@ -83,6 +83,7 @@
 #### **HTML Reports (`html/`)**
+* `html_multiplier_breakdown`: Multiplier Breakdown Report (Group Par)
 * `html_qso_comparison`: HTML QSO Comparison Report
 
@@ -100,4 +101,5 @@
 #### **Text Reports (`text/`)**
 * `comparative_continent_summary`: Comparative Continent QSO Summary
+* `text_multiplier_breakdown`: Multiplier Breakdown (Group Par)
 * `rate_sheet_comparison`: Comparative Rate Sheet
 * `comparative_score_report`: Comparative Score Report
@@ -106,4 +108,5 @@
 * `missed_multipliers`: Missed Multipliers Report
 * `multiplier_summary`: Multiplier Summary
+* `json_multiplier_breakdown`: JSON Multiplier Breakdown Artifact (Data Source)
 * `qso_comparison`: QSO Comparison Summary
 * `rate_sheet`: Hourly Rate Sheet
--- Docs/ProgrammersGuide.md
+++ Docs/ProgrammersGuide.md
@@ -2,5 +2,5 @@
 
-**Version: 0.126.0-Beta**
-**Date: 2025-12-18**
+**Version: 0.127.0-Beta**
+**Date: 2025-12-23**
 
@@ -155,4 +155,13 @@
 * **`contest_tools/utils/log_fetcher.py`**: A utility class used by the web view to scrape public contest 
 log archives (e.g., CQ WW) and download logs on-demand.
+* **`contest_tools/manifest_manager.py`**: Manages the `session_manifest.json`, providing a decoupled way for the UI to discover generated artifacts without hardcoding paths.
+
+### The Manifest & WORM Strategy
+To ensure the dashboard remains responsive even with large datasets, the application employs a **"Write Once, Read Many" (WORM)** strategy for expensive aggregations.
+
+1.  **Generation Phase:** During the initial analysis (`analyze_logs`), specific "Artifact Reports" (e.g., `json_multiplier_breakdown.py`) are executed. These reports do not produce human-readable text but instead serialize processed aggregation trees into JSON files.
+2.  **Hydration Phase:** When the user loads a dashboard view (e.g., `multiplier_dashboard`), the view uses the `ManifestManager` to locate the JSON artifact.
+3.  **Rendering:** The view hydrates its context directly from this pre-computed JSON, avoiding the need to re-parse Cabrillo logs or re-run aggregators on every page load.
 
 ---
--- web_app/analyzer/templates/analyzer/help_reports.html
+++ web_app/analyzer/templates/analyzer/help_reports.html
@@ -124,4 +124,10 @@
                     <hr>
 
+                    <h5 class="fw-bold text-dark mt-3">Multiplier Breakdown (Group Par)</h5>
+                    <p>Benchmarking against the group's potential.</p>
+                    <ul>
+                        <li><strong>Total Worked (Par):</strong> The total number of unique multipliers found by the entire group combined.</li>
+                        <li><strong>Delta:</strong> How far a specific station is from the Par. A negative number indicates missed opportunities that were present on the band (because someone else worked them).</li>
+                    </ul>
+                    <hr>
+
                     <h5 class="fw-bold text-dark mt-3">Missed Multipliers Report (`missed_multipliers`)</h5>
                     <p>The "Checklist" of costly missed opportunities.</p>
--- END DIFF ---

## 4. Affected Modules Checklist
* `Docs/ReportInterpretationGuide.md`
* `Docs/UsersGuide.md`
* `README.md`
* `Docs/ProgrammersGuide.md`
* `web_app/analyzer/templates/analyzer/help_reports.html`

## 5. Pre-Flight Check
* **Inputs:** Baseline versions of documentation and template.
* **Expected Outcome:**
    * Documentation accurately reflects the existence and purpose of the new "Group Par" reports.
    * Web help includes the new Multiplier Breakdown explanation.
    * Programmers Guide documents the WORM strategy.
* **Sanitization:** Checked for internal backticks in markdown updates.
* **Visual Compliance:** N/A (Text updates).

## 6. Post-Generation Verification
I will verify that the version numbers in the headers match the Implementation Plan and that the added text is free of typos.

**Next Action:** I will issue the standardized prompt for **Protocol 6.10 (Context Lock-In)**.