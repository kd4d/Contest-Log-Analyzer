# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.122.0-Beta

### 1. File Identification
* **File:** `web_app/analyzer/templates/base.html`
* **Baseline:** Version 0.102.0-Beta

### 2. Surgical Changes
* [cite_start]**Remove Global "New Analysis" Button:** Delete the `<a>` tag in the top navbar [cite: 1585] to prevent accidental session destruction from sub-pages.
* [cite_start]**Implement Session-Aware Menu:** Update the Offcanvas Menu [cite: 1586] to detect active sessions (`session_id` or `session_key`).
    * **State A (Active Session):** Show "Current Dashboard" as the primary action. Show "Start New Analysis" as a secondary, muted action.
    * **State B (No Session):** Show "New Analysis" as the primary action.

### 3. Surgical Change Verification
--- BEGIN DIFF ---
@@ -16,7 +16,6 @@
         <a class="navbar-brand fw-bold" href="{% url 'home' %}">
             <i class="bi bi-broadcast me-2"></i>Contest Log Analytics by KD4D
         </a>
-        <a href="{% url 'home' %}" class="btn btn-outline-light ms-auto fw-bold btn-sm">New Analysis</a>
       </div>
     </nav>
 
@@ -27,8 +26,20 @@
       </div>
       <div class="offcanvas-body">
         <ul class="nav flex-column">
-      
+          {% with active_session=session_id|default:session_key %}
+          {% if active_session %}
           <li class="nav-item">
+            <a class="nav-link active text-primary fw-bold" href="{% url 'dashboard_view' active_session %}">
+              <i class="bi bi-speedometer2 me-2"></i>Current Dashboard
+            </a>
+          </li>
+          <li class="nav-item">
+            <a class="nav-link text-muted" href="{% url 'home' %}">
+              <i class="bi bi-plus-circle me-2"></i>Start New Analysis
+            </a>
+          </li>
+          {% else %}
+          <li class="nav-item">
             <a class="nav-link active text-dark" href="{% url 'home' %}"><i class="bi bi-house-door me-2"></i>New Analysis</a>
-          </li>
+          </li>
+          {% endif %}
+          {% endwith %}
           <li class="nav-item mt-3">
             <span class="text-muted small text-uppercase fw-bold px-3">Help & Documentation</span>
--- END DIFF ---

### 4. Affected Modules Checklist
* `web_app/analyzer/templates/dashboard.html` (Retains its local button; no change needed).
* `web_app/analyzer/templates/analyzer/qso_dashboard.html` (Navbar button removed; "Back" button remains).
* `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` (Navbar button removed; "Back" button remains).

### 5. Pre-Flight Check
* **Expected Outcome:** The top-right "New Analysis" button will disappear from all pages. The side menu will intelligently route users back to their active dashboard if one exists.
* **Backward Compatibility:** Pages without session context (like the Home page) will default to the standard "New Analysis" menu item.
* **Visual Compliance:** Uses standard Bootstrap utility classes (`text-primary`, `text-muted`) consistent with the existing design.
* **Logic Verification:** The `default` filter handles the discrepancy between `session_id` (used in sub-dashboards) and `session_key` (used in the main dashboard context).

### 6. Post-Generation Verification
* I confirm the plan strictly follows the user's request to limit the proliferation of destructive buttons.
* Next Action Declaration included.