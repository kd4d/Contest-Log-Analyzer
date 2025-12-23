# ImplementationPlan.md

**Version:** 1.5.0
**Target:** 0.137.0-Beta

## 1. File Identification: contest_tools/reports/text_multiplier_breakdown.py
**Version:** 0.136.4-Beta

### Surgical Changes
1.  **Update `format_row` Helper**:
    * Modify the loop iterating over `all_calls`.
    * Calculate `delta = stats['count'] - total_worked` (or retrieve pre-calculated delta if available from `build_row`). Note: `MultiplierStatsAggregator.get_multiplier_breakdown_data` (Source 750) returns `delta` in the `stations` list.
    * Update the formatting string to append ` ({delta})` if `delta < 0`.
    * Increase the column width allocation in the loop to ensure alignment.

### Surgical Change Verification (diff)
__CODE_BLOCK__ python
--- BEGIN DIFF ---
@@ -107,11 +107,13 @@
             # Station columns
             # Re-implement row formatter to handle list input correctly
             # The previous code assumed station_dict was a dict.
             for i, call in enumerate(all_calls):
                 stats = station_dict[i] # station_dict is actually a list here
                 val = str(stats['count'])
-                row_str += f" {val:>10}"
+                delta = stats.get('delta', 0)
+                if delta < 0:
+                    val += f" ({delta})"
+                row_str += f" {val:>15}"
             return row_str
 
         # Header Row
         header = f"{'Scope':<25} {'Total':>8} {'Common':>8}"
         for call in all_calls:
-            header += f" {call:>10}"
+            header += f" {call:>15}"
         
         lines.append(header)
         lines.append("-" * len(header))
--- END DIFF ---
__CODE_BLOCK__

## 2. File Identification: contest_tools/reports/html_multiplier_breakdown.py (NEW)
**Version:** 0.1.0-Beta

### Surgical Changes
1.  **Create New Report**: Implement `class Report(ContestReport)` with `report_id = "html_multiplier_breakdown"`.
2.  **Logic**:
    * Inherit from `ContestReport`.
    * Use `MultiplierStatsAggregator` to fetch breakdown data.
    * Generate standard 3-line title using `get_standard_title_lines`.
    * Generate footer metadata using `get_cty_metadata`.
    * Render the `html_multiplier_breakdown.html` template with the data context.
    * Save file as `html_multiplier_breakdown_{callsigns}.html`.

### Surgical Change Verification (diff)
*New file, no diff.*

## 3. File Identification: contest_tools/templates/html_multiplier_breakdown.html (NEW)
**Version:** 0.1.0-Beta

### Surgical Changes
1.  **Create Template**: A standalone HTML template using Tailwind CSS (consistent with `html_qso_comparison`).
2.  **Structure**:
    * Header: Display `{{ report_title_lines }}`.
    * Table: Render the hierarchical matrix (Totals -> Low Bands -> High Bands).
    * Logic: Iterate through `breakdown_totals`, `low_bands_data`, and `high_bands_data` to render rows.
    * Styling: Highlight negative deltas in red.

### Surgical Change Verification (diff)
*New file, no diff.*

## 4. File Identification: web_app/analyzer/views.py
**Version:** 0.136.4-Beta

### Surgical Changes
1.  **Update `multiplier_dashboard` View**:
    * Retrieve `full_contest_title` from `dashboard_context.json`.
    * Add logic to discover `html_multiplier_breakdown_*.html` in the report root directory (`report_rel_path`).
    * Pass `full_contest_title` and `breakdown_html_url` to the template context.

### Surgical Change Verification (diff)
__CODE_BLOCK__ python
--- BEGIN DIFF ---
@@ -2067,6 +2067,7 @@
     if os.path.exists(context_path):
         with open(context_path, 'r') as f:
             d_ctx = json.load(f)
             persisted_logs = d_ctx.get('logs', [])
+            full_contest_title = d_ctx.get('full_contest_title', '')
 
     # Calculate optimal column width for scoreboard
     log_count = len(persisted_logs) if persisted_logs else 0
@@ -2079,6 +2080,12 @@
     for filename in os.listdir(text_dir):
         if filename.startswith(txt_breakdown_prefix) and filename.endswith(suffix):
             breakdown_txt_rel_path = os.path.join(report_rel_path, 'text', filename)
             break
+
+    # 5. Discover HTML Version of Breakdown
+    breakdown_html_rel_path = None
+    html_breakdown_prefix = "html_multiplier_breakdown_"
+    html_suffix = f"_{combo_id}.html"
+    # HTML reports are in the root report dir, not text/
+    report_abs_path = os.path.join(session_path, report_rel_path)
+    if os.path.exists(report_abs_path):
+        for filename in os.listdir(report_abs_path):
+            if filename.startswith(html_breakdown_prefix) and filename.endswith(html_suffix):
+                breakdown_html_rel_path = os.path.join(report_rel_path, filename)
+                break
 
     # 2. Scan and Group Reports
     # Expected format: missed_multipliers_{TYPE}_{COMBO_ID}.txt
@@ -2108,6 +2115,8 @@
         'breakdown_totals': breakdown_data['totals'],
         'low_bands_data': low_bands_data,
         'high_bands_data': high_bands_data,
         'all_calls': sorted([l['callsign'] for l in persisted_logs]),
         'breakdown_txt_url': breakdown_txt_rel_path,
+        'breakdown_html_url': breakdown_html_rel_path,
+        'full_contest_title': full_contest_title,
         'multipliers': sorted_mults,
         'is_solo': (log_count == 1),
     }
--- END DIFF ---
__CODE_BLOCK__

## 5. File Identification: web_app/analyzer/templates/analyzer/multiplier_dashboard.html
**Version:** 0.136.4-Beta

### Surgical Changes
1.  **Inject Title**: Add the `{{ full_contest_title }}` header above the table.
2.  **Update Icon Link**: Point the "Full Screen" icon to `breakdown_html_url` instead of `breakdown_txt_url`. Keep the TXT link as a secondary "Archive" option if desired, or replace it entirely. *Decision: Replace logic to prefer HTML if available, fallback to TXT.*

### Surgical Change Verification (diff)
__CODE_BLOCK__ html
--- BEGIN DIFF ---
@@ -1802,8 +1802,8 @@
     <div class="card mb-5 border shadow-sm">
         <div class="card-header bg-light d-flex justify-content-between align-items-center">
             <span class="fw-bold text-secondary"><i class="bi bi-grid-3x3-gap me-2"></i>Multiplier Breakdown (Group Par)</span>
-            {% if breakdown_txt_url %}
-            <a href="{% url 'view_report' session_id breakdown_txt_url %}" target="_blank" class="btn btn-sm btn-outline-secondary py-0" style="font-size: 0.8rem;">
-                <i class="bi bi-file-text me-1"></i>TXT View
-            </a>
-            {% endif %}
+            <div>
+                {% if breakdown_txt_url %}
+                <a href="{% url 'view_report' session_id breakdown_txt_url %}" target="_blank" class="btn btn-sm btn-link text-muted p-0 me-2" title="View Text Report">
+                    <i class="bi bi-file-text"></i>
+                </a>
+                {% endif %}
+                {% if breakdown_html_url %}
+                <a href="{% url 'view_report' session_id breakdown_html_url %}" target="_blank" class="btn btn-sm btn-link text-secondary p-0" title="Full Screen (HTML)">
+                    <i class="bi bi-box-arrow-up-right"></i>
+                </a>
+                {% endif %}
+            </div>
         </div>
         <div class="card-body p-4">
+            <div class="text-center mb-4">
+                <h4 class="fw-bold text-dark">{{ full_contest_title }}</h4>
+                <p class="text-muted small">Multiplier Analysis &bull; {{ all_calls|join:", " }}</p>
+            </div>
             
             <div class="table-responsive mb-4">
                 <table class="table table-sm table-hover mb-0 text-center align-middle border">
--- END DIFF ---
__CODE_BLOCK__

## 6. Pre-Flight Check
* **Inputs**: `manifest_bundle.txt`.
* **Expected Outcome**:
    * `text_multiplier_breakdown.py` produces wider columns with negative deltas.
    * `html_multiplier_breakdown.py` exists and generates a compliant HTML report.
    * `multiplier_dashboard` view passes `full_contest_title` and `breakdown_html_url`.
    * Dashboard UI shows the title and links to the HTML report.
* **Mental Walkthrough**:
    1.  User runs analysis.
    2.  `ReportGenerator` runs `html_multiplier_breakdown`.
    3.  User goes to Multiplier Dashboard.
    4.  View finds the HTML file and Context Title.
    5.  User sees "CQ WW CW 2024" header above the matrix.
    6.  User clicks the "pop-out" icon -> opens HTML report with Tailwind styling.
* **State Confirmation**: I will request `Confirmed` before delivery.