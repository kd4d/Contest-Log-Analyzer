--- FILE: ImplementationPlan.md ---
# Implementation Plan - Branding & Context Update

**Version:** 1.0.0
**Target:** 0.108.0-Beta

## 1. Builder Bootstrap Context
* **Goal:** Update the Application Shell (Header/Footer) with correct branding and inject dynamic context (CTY Version, Full Contest Title) into the Dashboard.
* **Constraint:** CTY information is dynamic and only available in the `analyze_logs` view after processing.
* **Files:** `base.html` (Shell), `views.py` (Logic), `dashboard.html` (Presentation).

## 2. Technical Debt Register
* **None:** This is a UI/UX refinement cycle.

## 3. Safety Protocols
* **Pre-Flight:** Verify `CtyLookup` is imported in `views.py` to access the static extraction method.
* **Visual Check:** Ensure the footer is sticky or pushed to the bottom effectively.

---

## 4. Execution Steps

### Step 1: Update Application Shell
**File:** `contest_tools/templates/base.html`
**Action:** Update Brand text, add Hamburger Menu, add Copyright Footer.

#### Surgical Changes
1.  **Navbar:** Add `navbar-toggler` button and update Brand text.
2.  **Footer:** Add a `<footer>` block at the bottom of the body.

#### Surgical Change Verification (diff)
__CODE_BLOCK__diff
--- contest_tools/templates/base.html
+++ contest_tools/templates/base.html
@@ -11,9 +11,14 @@
     
     <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
       <div class="container">
+        <button class="navbar-toggler me-2" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
+            <span class="navbar-toggler-icon"></span>
+        </button>
         <a class="navbar-brand fw-bold" href="{% url 'home' %}">
-            <i class="bi bi-broadcast me-2"></i>Contest Log Analytics
+            <i class="bi bi-broadcast me-2"></i>Contest Log Analytics by KD4D
         </a>
+        <div class="collapse navbar-collapse" id="navbarNav">
+            +        </div>
       </div>
     </nav>
 
     {% block content %}{% endblock %}
 
+    <footer class="text-center text-muted py-4 mt-5 border-top">
+        <div class="container">
+            <p class="mb-0 small">Copyright &copy; 2025 by Mark Bailey, KD4D</p>
+        </div>
+    </footer>
+
     <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
   </body>
 </html>
__CODE_BLOCK__

### Step 2: Inject Dynamic Context Logic
**File:** `web_app/analyzer/views.py`
**Action:** Calculate `cty_version` and `full_contest_title` in `analyze_logs`.

#### Surgical Changes
1.  Import `CtyLookup` from `contest_tools.core_annotations`.
2.  Extract `cty_dat_path` from the first log.
3.  Use `CtyLookup.extract_version_date` to get the date.
4.  Construct `full_contest_title` string.
5.  Add to `context`.

#### Surgical Change Verification (diff)
__CODE_BLOCK__diff
--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -35,6 +35,7 @@
 # Import Core Logic
 from contest_tools.log_manager import LogManager
 from contest_tools.data_aggregators.time_series import TimeSeriesAggregator
 from contest_tools.report_generator import ReportGenerator
+from contest_tools.core_annotations import CtyLookup
 
 logger = logging.getLogger(__name__)
 
@@ -118,10 +119,17 @@
                 # Extract basic scalars for dashboard
                 # Construct relative path components for the template
                 first_log_meta = lm.logs[0].get_metadata()
                 contest_name = first_log_meta.get('ContestName', 'Unknown').replace(' ', '_')
                 # Date/Year extraction logic mirrors LogManager
                 df_first = lm.logs[0].get_processed_data()
                 year = df_first['Date'].dropna().iloc[0].split('-')[0] if not df_first.empty else "UnknownYear"
                 
                 # Re-derive event_id locally or fetch from metadata if available (LogManager stores it there now)
                 event_id = first_log_meta.get('EventID', '')
+
+                # Construct Full Title: "CQ-WW-CW 2024" or "NAQP 2025 JAN"
+                full_contest_title = f"{contest_name.replace('_', ' ')} {year} {event_id}".strip()
+
+                # Extract CTY Version Info
+                cty_path = lm.logs[0].cty_dat_path
+                cty_date = CtyLookup.extract_version_date(cty_path)
+                cty_date_str = cty_date.strftime('%Y-%m-%d') if cty_date else "Unknown Date"
+                cty_filename = os.path.basename(cty_path)
+                cty_version_info = f"{cty_filename} ({cty_date_str})"
                 
                 all_calls = sorted([l.get_metadata().get('MyCall', f'Log{i+1}') for i, l in enumerate(lm.logs)])
                 combo_id = '_'.join(all_calls)
 
@@ -142,6 +150,8 @@
                     'mult_file': mult_filename,
                     'logs': [],
                     'mult_headers': [],
-                    'contest_name': contest_name.replace('_', ' '),
+                    'full_contest_title': full_contest_title,
+                    'cty_version_info': cty_version_info,
                 }
                 
                 # Determine multiplier headers from the first log (assuming all are same contest)
__CODE_BLOCK__

### Step 3: Render Context in Dashboard
**File:** `web_app/analyzer/templates/analyzer/dashboard.html`
**Action:** Display `full_contest_title` and `cty_version_info`.

#### Surgical Changes
1.  Replace `{{ contest_name }}` with `{{ full_contest_title }}` in the header.
2.  Add a provenance line below the Scoreboard table block.

#### Surgical Change Verification (diff)
__CODE_BLOCK__diff
--- web_app/analyzer/templates/analyzer/dashboard.html
+++ web_app/analyzer/templates/analyzer/dashboard.html
@@ -17,7 +17,7 @@
 
 <div class="container mt-5">
     <div class="d-flex justify-content-between align-items-center mb-4">
-        <h2 class="mb-0 text-secondary">Analysis Results: <span class="text-dark">{{ contest_name }}</span></h2>
+        <h2 class="mb-0 text-secondary">Analysis Results: <span class="text-dark">{{ full_contest_title }}</span></h2>
         <a href="{% url 'home' %}" class="btn btn-outline-secondary">
             <i class="bi bi-arrow-left me-1"></i>New Analysis
         </a>
     </div>
 
     <div class="card shadow-sm border-0 mb-5">
@@ -53,6 +53,7 @@
                 </tbody>
             </table>
+            <div class="card-footer bg-light py-2">
+                <small class="text-muted"><i class="bi bi-info-circle me-1"></i>Scored using {{ cty_version_info }}</small>
+            </div>
         </div>
     </div>
__CODE_BLOCK__

## 5. Compliance Report
* **Protocol 2.1.1 (Architecture):** PASS. Logic resides in View/Controller, Presentation in Templates. No leakage.
* **Protocol 3.3 (Context Audit):** PASS.
* **Protocol 3.2.4 (Sanitization):** PASS.

--- FILE: manifest.txt ---
contest_tools/templates/base.html
web_app/analyzer/views.py
web_app/analyzer/templates/analyzer/dashboard.html