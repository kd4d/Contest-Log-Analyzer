# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.121.0-Beta

**1. File: web_app/analyzer/views.py**
[cite_start]**Version:** 0.120.0-Beta [cite: 1674]

**Surgical Changes:**
1.  In `analyze_logs`, explicitly add the raw `contest_name` to the `context` dictionary before it is serialized to `dashboard_context.json`. This ensures the router has the raw data needed for decision-making.
2.  In `dashboard_view`, implement the routing logic:
    * Check if `contest_name` starts with "CQ-WW" (case-insensitive).
    * If NO, render `analyzer/dashboard_construction.html`.
    * If YES, proceed to render `analyzer/dashboard.html`.

**Surgical Change Verification:**
--- BEGIN DIFF ---
@@ -1698,4 +1698,5 @@
                     'full_contest_title': full_contest_title,
                     'cty_version_info': cty_version_info,
+                    'contest_name': contest_name,
                 }
                 
@@ -1717,4 +1718,9 @@
     with open(context_path, 'r') as f:
         context = json.load(f)
+
+    # Contest-Specific Routing
+    contest_name = context.get('contest_name', '').upper()
+    if not contest_name.startswith('CQ-WW'):
+        return render(request, 'analyzer/dashboard_construction.html', context)
     
     return render(request, 'analyzer/dashboard.html', context)
--- END DIFF ---

**Affected Modules Checklist:**
* `dashboard.html` (Implicitly affected by context availability, but no breaking changes).
* `dashboard_construction.html` (New file relies on this view).

**Pre-Flight Check:**
* **Inputs:** `web_app/analyzer/views.py` (0.120.0-Beta).
* **Expected Outcome:** `dashboard_view` correctly diverts non-CQ-WW logs to the construction page.
* [cite_start]**Mental Walkthrough:** Verified variable scope of `contest_name` in `analyze_logs` (defined at line 1693)[cite: 1693]. Verified `dashboard_context.json` persistence.
* **Syntax Validation:** Python 3.11 compliant.

---

**2. File: web_app/analyzer/templates/analyzer/dashboard_construction.html**
**Version:** New File
**Target:** 0.121.0-Beta

**Surgical Changes:**
1.  Create a new template extending `base.html`.
2.  Implement the "Successful Pivot" layout:
    * **Header:** Two-line format (`full_contest_title`).
    * **Intro:** Explanatory text confirming successful analysis.
    * **Primary Action:** "Download All Reports" button (Blue, Large).
    * **Visual:** Large `bi-cone-striped` icon (Warning Color) + "Coming Soon" text.
    * **Navigation:** "New Analysis" button.

**Surgical Change Verification:**
* New file creation. No diff.

**Pre-Flight Check:**
* **Inputs:** None (New File).
* **Expected Outcome:** A user-friendly "Coming Soon" page that provides immediate access to the data.
* **Visual Compliance:** Uses Bootstrap 5 classes matching `base.html`.

---

**3. File: web_app/analyzer/templates/analyzer/dashboard.html**
[cite_start]**Version:** 0.120.0-Beta [cite: 1736]

**Surgical Changes:**
1.  Insert the explanatory paragraph immediately below the main title container to confirm successful analysis before presenting the interactive tools.

**Surgical Change Verification:**
--- BEGIN DIFF ---
@@ -1737,4 +1737,5 @@
         <a href="{% url 'home' %}" class="btn btn-outline-secondary">
             <i class="bi bi-arrow-left me-1"></i>New Analysis
         </a>
     </div>
+    <p class="lead text-muted mb-5">Analysis complete. These interactive visualizations and reports were generated directly from your uploaded logs.</p>
 
     <div class="card shadow-sm border-0 mb-5">
--- END DIFF ---

**Affected Modules Checklist:**
* None.

**Pre-Flight Check:**
* **Inputs:** `web_app/analyzer/templates/analyzer/dashboard.html`.
* **Expected Outcome:** The standard dashboard now includes the requested explanatory text.
* **Visual Compliance:** Uses `lead text-muted` classes to match existing style guide.