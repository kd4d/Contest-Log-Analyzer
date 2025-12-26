# Implementation Plan - Fix QSO Dashboard Layout

**Version:** 1.0.0
**Target:** 0.141.0-Beta

### 1. File: `contest_tools/reports/chart_qso_breakdown.py`
**Baseline:** Version 0.140.0-Beta

**Surgical Changes:**
1.  In `make_subplots`: Remove the `subplot_titles` argument entirely to eliminate the floating text that overlaps with the main header.
2.  In `make_subplots`: Decrease `vertical_spacing` from `0.08` to `0.05` to maximize the vertical space available for the bars within the constrained dashboard height.
3.  Inside the band iteration loop (`for i, band in enumerate(bands):`): Add `fig.update_xaxes(title_text=band, row=row, col=col)` to anchor the band label to the bottom of each individual subplot.
4.  Update the HTML layout override: Change `margin=dict(t=90, b=70, l=50, r=50)` to `margin=dict(t=100, b=40, l=50, r=50)` to ensure title clearance while maximizing chart area.
5.  Ensure `fig.layout.height` and `fig.layout.width` are explicitly set to `None` before HTML export to enforce responsiveness.

--- BEGIN DIFF ---
--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -112,5 +112,4 @@
             rows=rows, 
             cols=cols, 
             shared_yaxes=True,
-            subplot_titles=[f"Band: {b}" for b in bands],
-            vertical_spacing=0.08
+            vertical_spacing=0.05
         )
 
@@ -140,4 +139,5 @@
                     row=row, col=col
                 )
+            fig.update_xaxes(title_text=band, row=row, col=col)
 
         # Standard Layout Application
@@ -187,5 +187,5 @@
         
         # Optimize margins for dashboard display
-        fig.update_layout(margin=dict(t=90, b=70, l=50, r=50))
+        fig.update_layout(margin=dict(t=100, b=40, l=50, r=50))
         
         config = {
--- END DIFF ---

### 2. File: `web_app/analyzer/templates/analyzer/qso_dashboard.html`
**Baseline:** Version 0.139.8-Beta

**Surgical Changes:**
1.  Add `overflow: hidden;` to the style attribute of the `frame-breakdown` iframe to prevent scrollbars caused by browser default margins.

--- BEGIN DIFF ---
--- web_app/analyzer/templates/analyzer/qso_dashboard.html
+++ web_app/analyzer/templates/analyzer/qso_dashboard.html
@@ -124,5 +124,5 @@
                         </div>
                         <div class="card-body p-0" style="height: 600px;">
-                            <iframe id="frame-breakdown" src="" style="width: 100%; height: 100%; border: none;"></iframe>
+                            <iframe id="frame-breakdown" src="" style="width: 100%; height: 100%; border: none; overflow: hidden;"></iframe>
                         </div>
                     </div>
--- END DIFF ---

### 3. Affected Modules Checklist
* `contest_tools/reports/chart_qso_breakdown.py`
* `web_app/analyzer/templates/analyzer/qso_dashboard.html`

### 4. Pre-Flight Check
* **Expected Outcome:** The QSO Breakdown chart will display x-axis labels (Band names) at the bottom of each subplot. The chart header will no longer overlap subplot titles. The dashboard pane will no longer display vertical scrollbars.
* **Mental Walkthrough:**
    * Plotly generates subplots without titles.
    * Loop iterates bands, adding bars.
    * Loop adds x-axis title for each specific subplot.
    * Margins are set to t=100 (clearance) and b=40 (labels).
    * HTML is generated responsive.
    * Dashboard iframe clips any overflow 16px margin from body.
* **Verification:** Visual inspection of dashboard and PNG output.