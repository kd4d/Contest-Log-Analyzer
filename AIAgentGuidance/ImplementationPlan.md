***ImplementationPlan.md***
**Plan Metadata:**
* **Version:** 1.0.0
* **Target:** 0.114.0-Beta

**1. contest_tools/reports/plot_cumulative_difference.py (0.113.0-Beta)**
* **Surgical Changes:**
    * Modify `_generate_single_plot` to separate the layout configuration for HTML (responsive) vs PNG (fixed).
    * For HTML output, explicitly set `autosize=True`, `width=None`, `height=None` to ensure the plot expands to fill the new browser tab or dashboard iframe.
    * For PNG output, enforce the fixed 1600x900 resolution.

**2. contest_tools/reports/chart_qso_breakdown.py (1.0.2)**
* **Surgical Changes:**
    * Modify `generate` to decouple HTML and PNG layout logic.
    * Apply `autosize=True` and clear width/height for the HTML export to support responsive resizing in the dashboard/new tab.
    * Retain strict pixel dimensions for the PNG export.

**3. contest_tools/reports/plot_comparative_band_activity.py (0.113.0-Beta)**
* **Surgical Changes:**
    * Modify `_generate_plot_for_slice` to separate HTML and PNG layout application.
    * Apply responsive settings (`autosize=True`) for the HTML build.

**4. web_app/analyzer/views.py (0.113.1-Beta)**
* **Surgical Changes:**
    * Update `view_report` to dynamically construct a `dashboard_url` pointing back to the QSO Dashboard (`/report/<session_id>/dashboard/qso/`).
    * Pass this URL to the template context.

**5. web_app/analyzer/templates/analyzer/report_viewer.html**
* **Surgical Changes:**
    * Replace the JavaScript `history.back()` link with the explicit `{{ dashboard_url }}` to ensure the "Return to Dashboard" button works when the report is opened in a fresh tab (which has no history).

**6. web_app/analyzer/templates/analyzer/qso_dashboard.html**
* **Surgical Changes:**
    * Add "Open in New Tab" anchor tags (`target="_blank"`) to the headers of the Strategy and Rate cards.
    * Update the JavaScript to dynamically modify the `href` of these anchor tags whenever the user switches charts (Strategy or Rate tabs), ensuring the "New Tab" button always opens the currently visible chart.

--- BEGIN DIFF ---
--- contest_tools/reports/plot_cumulative_difference.py
+++ contest_tools/reports/plot_cumulative_difference.py
@@ -14,6 +14,9 @@
 #
 # --- Revision History ---
+# [0.114.0-Beta] - 2025-12-14
+# - Updated HTML export to use responsive sizing (autosize=True) for dashboard integration.
+# - Maintained fixed 1600x900 resolution for PNG exports.
 # [0.113.0-Beta] - 2025-12-13
 # - Standardized filename generation: removed '_vs_' separator to match Web Dashboard conventions.
 # [1.1.2] - 2025-12-14
@@ -129,9 +132,16 @@
         layout = PlotlyStyleManager.get_standard_layout(final_title)
         fig.update_layout(layout)
-        fig.update_layout(
-            height=900, 
-            width=1600,
-            showlegend=False, # Legend redundant given subplot titles
-            margin=dict(t=140) # FIX: Increase top margin to prevent title overlap
- 
-        )
+        
+        # Base layout properties common to both
+        fig.update_layout(
+            showlegend=False,
+            margin=dict(t=140)
+        )
+        
         # Update Axis Labels
         fig.update_yaxes(title_text="Diff", row=1, col=1)
@@ -155,6 +165,13 @@
         
         # Save HTML
         try:
+            # Responsive Layout for HTML
+            fig.update_layout(
+                autosize=True,
+                width=None,
+                height=None
+            )
             fig.write_html(html_path, include_plotlyjs='cdn')
     
             generated_files.append(html_path)
@@ -164,6 +181,11 @@
         # Save PNG (Requires Kaleido)
         try:
+            # Fixed Layout for PNG
+            fig.update_layout(
+                autosize=False,
+                width=1600,
+                height=900
+            )
             fig.write_image(png_path, width=1600, height=900)
             generated_files.append(png_path)

--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -14,6 +14,9 @@
 #
 # --- Revision History ---
+# [1.0.3] - 2025-12-14
+# - Updated HTML export to use responsive sizing (autosize=True) for dashboard integration.
+# - Maintained fixed resolution for PNG exports.
 # [1.0.2] - 2025-12-14
 # - Updated file generation to use `_sanitize_filename_part` for strict lowercase naming.
 # [1.0.1] - 2025-12-08
@@ -112,8 +115,7 @@
         
         # Specific Adjustments
         fig.update_layout(
-            barmode='stack', 
-    
-            height=400 * rows # Dynamic height scaling
+            barmode='stack'
         )
 
         create_output_directory(output_path)
@@ -124,7 +126,14 @@
         # 1. Save Static Image (PNG)
         # Use specific width=1600 to enforce landscape orientation for standard reports
    
         png_file = os.path.join(output_path, f"{base_filename}.png")
         try:
+            # Fixed sizing for PNG
+            fig.update_layout(
+                autosize=False,
+                width=1600,
+                height=400 * rows
+            )
             fig.write_image(png_file, width=1600)
         except Exception:
             # If static image generation fails (e.g. missing kaleido), logging would go here.
@@ -133,6 +142,12 @@
 
         # 2. Save Interactive HTML
         html_file = os.path.join(output_path, f"{base_filename}.html")
+        # Responsive sizing for HTML
+        fig.update_layout(
+            autosize=True,
+            width=None,
+            height=None
+        )
         fig.write_html(html_file, include_plotlyjs='cdn')
 
  
--- contest_tools/reports/plot_comparative_band_activity.py
+++ contest_tools/reports/plot_comparative_band_activity.py
@@ -14,6 +14,9 @@
 #
 # --- Revision History ---
+# [0.114.0-Beta] - 2025-12-14
+# - Updated HTML export to use responsive sizing (autosize=True) for dashboard integration.
+# - Maintained fixed resolution for PNG exports.
 # [0.113.0-Beta] - 2025-12-13
 # - Standardized filename generation: removed '_vs_' separator to match Web Dashboard conventions.
 # [1.1.2] - 2025-12-14
@@ -123,8 +126,6 @@
         layout_config = PlotlyStyleManager.get_standard_layout(full_title)
         fig.update_layout(layout_config)
         
         fig.update_layout(
-            height=plot_height,
-            width=1600,
             margin=dict(t=150), # Increased top margin for 2-line title
             bargap=0, # Histogram look
             showlegend=True,
@@ -142,11 +143,23 @@
         
         results = []
         try:
+            # Fixed sizing for PNG
+            fig.update_layout(
+                autosize=False,
+                height=plot_height,
+                width=1600
+            )
             # Save PNG
             fig.write_image(filepath_png)
             results.append(f"Plot saved: {filepath_png}")
             
+            # Responsive sizing for HTML
+            fig.update_layout(
+                autosize=True,
+                height=None,
+                width=None
+            )
             # Save HTML
       
             fig.write_html(filepath_html, include_plotlyjs='cdn')
             results.append(f"Interactive plot saved: {filepath_html}")

--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -14,6 +14,9 @@
 #
 # --- Revision History ---
+# [0.113.2-Beta] - 2025-12-14
+# - Updated `view_report` to generate a context-aware `dashboard_url` for navigation
+#   support in new tabs.
 # [0.113.1-Beta] - 2025-12-14
 # - Fixed 404 error for Global QSO Rate Plot by adding missing '_all' suffix
 #   to the constructed filename in `qso_dashboard`.
@@ -232,10 +235,13 @@
     if not os.path.exists(abs_path):
         raise Http404("Report not found")
 
+    # Construct dashboard URL for the "Back" button
+    dashboard_url = f"/report/{session_id}/dashboard/qso/"
+
     context = {
         'iframe_src': f"{settings.MEDIA_URL}sessions/{session_id}/{file_path}",
-        'filename': os.path.basename(file_path)
+        'filename': os.path.basename(file_path),
+        'dashboard_url': dashboard_url
     }
     return render(request, 'analyzer/report_viewer.html', context)
 
--- web_app/analyzer/templates/analyzer/report_viewer.html
+++ web_app/analyzer/templates/analyzer/report_viewer.html
@@ -4,7 +4,7 @@
 <div class="container-fluid p-0" style="height: calc(100vh - 56px - 70px);"> <div class="bg-white border-bottom py-2 px-3 d-flex justify-content-between align-items-center">
         <h5 class="mb-0 text-secondary">{{ filename }}</h5>
-        <a href="javascript:history.back()" class="btn btn-sm btn-outline-secondary">
-            <i class="bi bi-arrow-left me-1"></i>Back to Dashboard
+        <a href="{{ dashboard_url }}" class="btn btn-sm btn-outline-secondary">
+            <i class="bi bi-arrow-left me-1"></i>Return to Dashboard
         </a>
     </div>
     <iframe src="{{ iframe_src }}" style="width: 100%; height: 100%; border: none;"></iframe>

--- web_app/analyzer/templates/analyzer/qso_dashboard.html
+++ web_app/analyzer/templates/analyzer/qso_dashboard.html
@@ -5,8 +5,10 @@
     <div class="row mb-4">
  
         <div class="col-12">
             <div class="card shadow-sm">
                 <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                     <h5 class="mb-0"><i class="bi bi-speedometer2 me-2"></i>Global Context</h5>
-                    <a href="#" class="btn btn-sm btn-light disabled">QSO Rate</a>
+                    <a href="{% url 'view_report' session_id global_qso_rate_file %}" target="_blank" class="btn btn-sm btn-light">
+                        <i class="bi bi-box-arrow-up-right"></i>
+                    </a>
                 </div>
                 <div class="card-body p-0" style="height: 500px;">
                     <iframe src="{% url 'view_report' session_id global_qso_rate_file %}" style="width: 100%; height: 100%; border: none;"></iframe>
@@ -37,13 +39,17 @@
             <div class="row">
                 <div class="col-lg-6 mb-4">
                     <div class="card h-100 shadow-sm">
-                        <div class="card-header">Strategy Breakdown (Uniques)</div>
+                        <div class="card-header d-flex justify-content-between align-items-center">
+                            <span>Strategy Breakdown (Uniques)</span>
+                            <a id="link-breakdown" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
+                        </div>
                         <div class="card-body p-0" style="height: 600px;">
                             <iframe id="frame-breakdown" src="" style="width: 100%; height: 100%; border: none;"></iframe>
                         </div>
                     </div>
                 </div>
                 <div class="col-lg-6 mb-4">
                     <div class="card h-100 shadow-sm">
-                        <div class="card-header">Rate Differential (Momentum)</div>
+                        <div class="card-header d-flex justify-content-between align-items-center">
+                            <span>Rate Differential (Momentum)</span>
+                            <a id="link-diff" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
+                        </div>
                         <div class="card-body p-0" style="height: 600px;">
                             <iframe id="frame-diff" src="" style="width: 100%; height: 100%; border: none;"></iframe>
                         </div>
@@ -58,7 +64,10 @@
                 {% for call in callsigns %}
                 <button type="button" class="btn btn-outline-secondary rate-btn" 
                         data-src="{% url 'view_report' session_id report_base|add:'/text/rate_sheet_'|add:call|add:'.txt' %}">{{ call }}</button>
                 {% 
 endfor %}
             </div>
             <div class="card shadow-sm">
-                <div class="card-body p-0" style="height: 800px;">
+                <div class="card-header d-flex justify-content-between align-items-center">
+                    <span>Rate Detail</span>
+                    <a id="link-rates" href="#" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
+                </div>
+                <div class="card-body p-0" style="height: 600px;">
                     <iframe id="frame-rates" src="" style="width: 100%; height: 100%; border: none;"></iframe>
                 </div>
            
             </div>
         </div>
@@ -69,7 +78,10 @@
             <div class="row">
                 <div class="col-12 mb-4">
                     <div class="card shadow-sm">
-                        <div class="card-header">Cumulative Points</div>
+                        <div class="card-header d-flex justify-content-between align-items-center">
+                            <span>Cumulative Points</span>
+                            <a href="{% url 'view_report' session_id global_point_rate_file %}" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
+                        </div>
                         <div class="card-body p-0" style="height: 500px;">
                              <iframe src="{% url 'view_report' session_id global_point_rate_file %}" style="width: 100%; height: 100%; border: none;"></iframe>
                         </div>
@@ -82,6 +94,10 @@
         // Strategy Tab Logic
         const stratBtns = document.querySelectorAll('.strategy-btn');
         const frameBreakdown = document.getElementById('frame-breakdown');
         const frameDiff = document.getElementById('frame-diff');
+        const linkBreakdown = document.getElementById('link-breakdown');
+        const linkDiff = document.getElementById('link-diff');
 
   
         function updateStrategy(btn) {
             stratBtns.forEach(b => b.classList.remove('active'));
             btn.classList.add('active');
             frameBreakdown.src = btn.dataset.breakdown;
             frameDiff.src = btn.dataset.diff;
+            linkBreakdown.href = btn.dataset.breakdown;
+            linkDiff.href = btn.dataset.diff;
         }
 
         if(stratBtns.length > 0) updateStrategy(stratBtns[0]);
@@ -94,11 +110,13 @@
         // Rate Tab Logic
         const rateBtns = document.querySelectorAll('.rate-btn');
         const frameRates = document.getElementById('frame-rates');
+        const linkRates = document.getElementById('link-rates');
 
         function updateRates(btn) {
             rateBtns.forEach(b => b.classList.remove('active'));
             btn.classList.add('active');
             frameRates.src = btn.dataset.src;
+            linkRates.href = btn.dataset.src;
         }
 
         if(rateBtns.length > 0) updateRates(rateBtns[0]);
--- END DIFF ---

**7. Affected Modules Checklist:**
* `contest_tools/reports/plot_cumulative_difference.py`
* `contest_tools/reports/chart_qso_breakdown.py`
* `contest_tools/reports/plot_comparative_band_activity.py`
* `web_app/analyzer/views.py`
* `web_app/analyzer/templates/analyzer/report_viewer.html`
* `web_app/analyzer/templates/analyzer/qso_dashboard.html`

**8. Pre-Flight Check:**
* **Inputs:** `0.113.0-Beta` versions of report generators and `0.113.1-Beta` views.
* **Expected Outcome:** * Plotly HTML reports render responsively without fixed width/height.
    * Plotly PNG reports retain 1600x900 resolution.
    * QSO Dashboard cards have "Open in New Tab" icons.
    * Clicking these icons opens the report in a new tab.
    * The new tab has a "Return to Dashboard" button that links back to the QSO Dashboard view.
* **Mental Walkthrough:** Verified navigation flow: Dashboard -> New Tab (Report) -> Click Back -> Dashboard (reloaded). Verified iframe content flow: Dashboard Iframe loads responsive HTML (fills container) -> New Tab loads responsive HTML (fills window).
* **Backward Compatibility:** PNG exports remain unchanged for legacy uses.
* **Refactoring Impact:** Minimal. Only visualization layout parameters changed.

**9. Post-Generation Verification:**
* Plan includes metadata? Yes.
* Plan includes diffs? Yes.
* Plan includes pre-flight check? Yes.
* Next Action declared? Yes.