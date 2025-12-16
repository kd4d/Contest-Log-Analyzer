# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.120.1-Beta

## 1. File Identification
**File:** `web_app/analyzer/templates/analyzer/dashboard_construction.html`
**Baseline:** Version 0.121.0-Beta (Inferred from bundle context)

## 2. Surgical Changes
This redesign splits the single "Under Construction" card into two distinct tiers:
1.  **The "Success" Pane (Top):** Focuses on the successful completion of the backend analysis and provides the download button. Uses the new copy requested.
2.  **The "Coming Soon" Pane (Bottom):** Uses a dark gradient background to implement the "classier" aesthetic for the roadmap messaging.

**Change 1: Redesign the Layout**
* Replace the single `.card` container with two distinct `.row` blocks.
* **Top Block:** White background, standard text. Headline "Analysis Successful".
* **Bottom Block:** Dark gradient background (`linear-gradient(45deg, #141e30, #243b55)`), white text.

__CODE_BLOCK__diff
--- BEGIN DIFF ---
@@ -10,18 +10,19 @@
     <div class="row justify-content-center text-center">
         <div class="col-lg-8">
-            <div class="card shadow-sm border-0 py-5">
-                <div class="card-body">
-                    <i class="bi bi-cone-striped text-warning mb-4" style="font-size: 5rem;"></i>
-                    <h3 class="fw-bold text-dark mb-3">Interactive Dashboard Coming Soon</h3>
-                    <p class="lead text-muted mb-4">
-                        Analysis complete. The interactive dashboard for <strong>{{ contest_name }}</strong> is currently under development.
-                        <br>
-                        However, your full report package has been generated and is ready for download.
-                    </p>
-
-                    <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
-                        <a href="{% url 'download_all_reports' session_key %}" class="btn btn-primary btn-lg px-5">
-                            <i class="bi bi-file-earmark-zip me-2"></i>Download All Reports
-                        </a>
-                    </div>
-                    <p class="text-muted small mt-3">Contains all Charts (PNG/HTML) and Text Reports generated from your logs.</p>
-                </div>
-            </div>
+            +            <div class="card shadow-sm border-0 mb-5">
+                <div class="card-body p-5">
+                    <h2 class="fw-bold text-success mb-3"><i class="bi bi-check-circle-fill me-2"></i>Analysis Successful</h2>
+                    <p class="lead text-muted mb-4">
+                        We have successfully processed your logs and generated the full suite of static reports. 
+                        While the interactive strategy board for <strong>{{ contest_name }}</strong> is being built, your complete data package is ready now.
+                    </p>
+                    <a href="{% url 'download_all_reports' session_key %}" class="btn btn-primary btn-lg px-5 shadow-sm">
+                        <i class="bi bi-file-earmark-zip me-2"></i>Download All Reports
+                    </a>
+                </div>
+            </div>
+
+            +            <div class="card border-0 shadow-sm text-white" style="background: linear-gradient(45deg, #141e30, #243b55); min-height: 300px;">
+                <div class="card-body d-flex flex-column justify-content-center align-items-center p-5">
+                    <h1 class="display-5 fw-bold mb-3">Coming Soon</h1>
+                    <hr class="border-white opacity-50 w-25 mb-4">
+                    <p class="lead fw-light">
+                        We are currently tailoring the interactive widgets for the specific scoring rules of {{ contest_name }}.<br>
+                        Watch this space.
+                    </p>
+                </div>
+            </div>
         </div>
     </div>
--- END DIFF ---
__CODE_BLOCK__

---

## 1. File Identification
**File:** `web_app/analyzer/templates/analyzer/dashboard.html`
**Baseline:** Version 0.121.0-Beta (Inferred from bundle context)

## 2. Surgical Changes
This update standardizes the description in the "Raw Data Access" pane to match the first sentence of the Construction page, as requested.

**Change 1: Update Descriptive Text**
* Replace "Contains all Charts (PNG/HTML) and Text Reports." with "We have successfully processed your logs and generated the full suite of static reports."

__CODE_BLOCK__diff
--- BEGIN DIFF ---
@@ -118,3 +118,3 @@
                 <a href="{% url 'download_all_reports' session_key %}" class="btn btn-primary btn-lg">
                     <i class="bi bi-file-earmark-zip me-2"></i>Download All Reports
                 </a>
-                <p class="text-muted x-small mt-2 mb-0">Contains all Charts (PNG/HTML) and Text Reports.</p>
+                <p class="text-muted small mt-3 mb-0">We have successfully processed your logs and generated the full suite of static reports.</p>
             </div>
--- END DIFF ---
__CODE_BLOCK__

## 4. Affected Modules Checklist
* `dashboard_construction.html` (Redesign)
* `dashboard.html` (Copy Update)

## 5. Pre-Flight Check
* **Inputs:** `contest_name` and `session_key` context variables.
* **Expected Outcome:** * Non-CQ-WW contests show a professional, split-view page (Success top, Dark gradient "Coming Soon" bottom).
    * CQ-WW contests show the updated text in the bottom "Raw Data" card.
* **Safety:** HTML/CSS only; no logic changes.
* **Visual Compliance:** Uses standard Bootstrap 5 classes + inline CSS for the gradient.