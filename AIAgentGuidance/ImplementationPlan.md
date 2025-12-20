# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.126.1-Beta

## 1. Overview
This plan focuses exclusively on **Phase 1: The "Solo Audit" Sprint**. It hardens the existing dashboard for single-log uploads and introduces the **Correlation Analysis** report to provide descriptive insights without overstepping into prescriptive efficiency metrics.

The goal is to create a robust, "Solo-Proof" experience that prepares the groundwork for future modularity without introducing structural risks now.

## 2. Surgical Changes

### A. New Report Module: `contest_tools/reports/plot_correlation_analysis.py`
* **Purpose:** Generates two side-by-side scatter plots (Rate vs. Run % and New Mults vs. Run %).
* **Logic:**
    * Uses `TimeSeriesAggregator` to get hourly data.
    * Computes hourly deltas (`.diff()`) for `run_qso_count`, `sp_unk_qso_count`, and `total_mults`.
    * Calculates `Run % = Run / (Run + S&P + Unk)`.
    * **Filter:** None (All hours plotted, even noise at origin, per user instruction).
    * **Visuals:** Plotly scatter traces, colored by Band (if single-band data available) or just simple markers.
    * **Output:** Saves interactive HTML and static PNG.

### B. View Logic: `web_app/analyzer/views.py`
* **Function:** `analyze_logs`
    * Update to register the new report filename (`correlation_file`) in the context.
* **Function:** `qso_dashboard`
    * Implement `is_solo` detection: `is_solo = (len(callsigns_safe) == 1)`.
    * If `is_solo`, suppress `matchups` generation.
    * Pass `is_solo` to template.
* **Function:** `multiplier_dashboard`
    * Implement `is_solo` detection.
    * If `is_solo`, scan for `multiplier_summary` files instead of `missed_multipliers`.
    * Map these to the `missed` key (hijacking the slot) to leverage existing template logic.

### C. Template Logic: `web_app/analyzer/templates/analyzer/qso_dashboard.html`
* **Tab Navigation:**
    * Add new "Correlations" tab.
    * If `is_solo`: Hide "Pairwise Strategy" tab. Make "Correlations" or "Rate Detail" the active default.
* **Content Panes:**
    * Add `#correlations` pane containing the new report iframe.
    * Wrap `#strategy` pane in `{% if not is_solo %}`.

### D. Template Logic: `web_app/analyzer/templates/analyzer/multiplier_dashboard.html`
* **Card Rendering:**
    * Update header to "Multiplier Matrix Reports" if `is_solo`.
    * Change text color style from `text-danger` (Red) to `text-info` (Blue) for solo mode to indicate "Information" vs "Missed Opportunity".

## 3. Surgical Change Verification (`diff`)

--- BEGIN DIFF ---
--- /dev/null
+++ contest_tools/reports/plot_correlation_analysis.py
@@ -0,0 +1,135 @@
+# contest_tools/reports/plot_correlation_analysis.py
+#
+# Purpose: Generates scatter plots correlating Run % with QSO Rate and Multiplier Yield.
+#          Descriptive analytics for the "Solo Audit".
+#
+# Author: Gemini AI
+# Date: 2025-12-18
+# Version: 1.0.0
+#
+# Copyright (c) 2025 Mark Bailey, KD4D
+# License: Mozilla Public License, v. 2.0
+
+import pandas as pd
+import plotly.graph_objects as go
+from plotly.subplots import make_subplots
+import os
+from typing import List
+
+from ..contest_log import ContestLog
+from .report_interface import ContestReport
+from ._report_utils import create_output_directory, _sanitize_filename_part, save_debug_data
+from ..data_aggregators.time_series import TimeSeriesAggregator
+from ..styles.plotly_style_manager import PlotlyStyleManager
+
+class Report(ContestReport):
+    report_id = "plot_correlation_analysis"
+    report_name = "Correlation Analysis"
+    report_type = "plot"
+    supports_single = True
+    supports_multi = True
+    
+    def generate(self, output_path: str, **kwargs) -> str:
+        agg = TimeSeriesAggregator(self.logs)
+        ts_data = agg.get_time_series_data()
+        
+        # Grid: 1 Row per Log, 2 Cols (Rate vs Run%, Mults vs Run%)
+        num_logs = len(self.logs)
+        fig = make_subplots(
+            rows=num_logs, cols=2,
+            subplot_titles=["Rate vs Run %", "New Mults vs Run %"] * num_logs,
+            vertical_spacing=0.1
+        )
+        
+        all_calls = sorted(list(ts_data['logs'].keys()))
+        
+        for i, call in enumerate(all_calls):
+            row = i + 1
+            log_entry = ts_data['logs'][call]
+            
+            # Extract Cumulative Series
+            # We need to re-create the Series to use .diff()
+            idx = pd.to_datetime(ts_data['time_bins'])
+            s_run = pd.Series(log_entry['cumulative']['run_qsos'], index=idx)
+            s_sp = pd.Series(log_entry['cumulative']['sp_unk_qsos'], index=idx)
+            s_mults = pd.Series(log_entry['cumulative']['mults'], index=idx)
+            
+            # Calculate Hourly Deltas
+            h_run = s_run.diff().fillna(s_run.iloc[0])
+            h_sp = s_sp.diff().fillna(s_sp.iloc[0])
+            h_mults = s_mults.diff().fillna(s_mults.iloc[0])
+            h_total = h_run + h_sp
+            
+            # Calculate Run % (Safe Division)
+            # Avoid division by zero
+            h_run_pct = (h_run / h_total).fillna(0) * 100
+            
+            # Color by Rate Intensity? Or just standard color
+            color = PlotlyStyleManager._COLOR_PALETTE[i % len(PlotlyStyleManager._COLOR_PALETTE)]
+            
+            # Trace 1: Rate vs Run %
+            fig.add_trace(
+                go.Scatter(
+                    x=h_run_pct,
+                    y=h_total,
+                    mode='markers',
+                    name=f"{call} Rate",
+                    marker=dict(color=color, size=8, opacity=0.7),
+                    hovertemplate="Run: %{x:.1f}%<br>Rate: %{y}<extra></extra>",
+                    legendgroup=call
+                ),
+                row=row, col=1
+            )
+            
+            # Trace 2: Mults vs Run %
+            fig.add_trace(
+                go.Scatter(
+                    x=h_run_pct,
+                    y=h_mults,
+                    mode='markers',
+                    name=f"{call} Mults",
+                    marker=dict(color=color, size=8, symbol='diamond', opacity=0.7),
+                    hovertemplate="Run: %{x:.1f}%<br>New Mults: %{y}<extra></extra>",
+                    legendgroup=call,
+                    showlegend=False
+                ),
+                row=row, col=2
+            )
+            
+            # Update Axes Titles
+            fig.update_xaxes(title_text=f"{call} Run %", range=[-5, 105], row=row, col=1)
+            fig.update_xaxes(title_text=f"{call} Run %", range=[-5, 105], row=row, col=2)
+            fig.update_yaxes(title_text="Hourly Rate", row=row, col=1)
+            fig.update_yaxes(title_text="Hourly Mults", row=row, col=2)
+
+        # Layout
+        title = "Correlation Analysis: Operational Efficiency"
+        layout = PlotlyStyleManager.get_standard_layout(title)
+        fig.update_layout(layout)
+        fig.update_layout(
+            height=400 * num_logs,
+            width=1200,
+            showlegend=True
+        )
+        
+        create_output_directory(output_path)
+        filename_calls = '_'.join([_sanitize_filename_part(c) for c in all_calls])
+        base_filename = f"{self.report_id}_{filename_calls}"
+        
+        html_path = os.path.join(output_path, f"{base_filename}.html")
+        png_path = os.path.join(output_path, f"{base_filename}.png")
+        
+        # Save
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
+        
+        try:
+            fig.write_image(png_path)
+        except:
+            pass
+            
+        return html_path

--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -1630,6 +1630,7 @@
     # CRITICAL: Filenames on disk are lowercased by ReportGenerator. We must match that.
     animation_filename = f"interactive_animation_{combo_id.lower()}.html"
     plot_filename = f"qso_rate_{combo_id.lower()}.html"
+    correlation_filename = f"plot_correlation_analysis_{combo_id.lower()}.html"
     
     # Note: Multiplier filename removed here. It is now dynamically resolved in multiplier_dashboard view.
 
@@ -1637,6 +1638,7 @@
         'session_key': session_key,
         'report_url_path': report_url_path,
         'animation_file': animation_filename,
         'plot_file': plot_filename,
+        'correlation_file': correlation_filename,
         'logs': [],
         'mult_headers': [],
    
@@ -1653,8 +1655,13 @@
     suffix = f"_{combo_id}.txt"
     multipliers = {}
 
+    # In Solo Mode, we show 'multiplier_summary' (The Matrix) instead of 'missed_multipliers'
+    # We map it to the 'missed' key so the template renders it in the card slot.
+    target_prefix = 'multiplier_summary_' if log_count == 1 else 'missed_multipliers_'
+
     for filename in os.listdir(text_dir):
         if not filename.endswith(suffix):
             continue
         
         mult_type = None
-        if filename.startswith('missed_multipliers_'):
-            mult_type = filename.replace('missed_multipliers_', '').replace(suffix, '').replace('_', ' ').title()
-            report_key = 'missed'
-        elif filename.startswith('multiplier_summary_'):
+        if filename.startswith(target_prefix):
+            mult_type = filename.replace(target_prefix, '').replace(suffix, '').replace('_', ' ').title()
+            report_key = 'missed' # Hijack 'missed' slot for display
+        elif filename.startswith('multiplier_summary_') and log_count > 1:
             mult_type = filename.replace('multiplier_summary_', '').replace(suffix, '').replace('_', ' ').title()
             report_key = 'summary'
         
@@ -1674,6 +1681,7 @@
         'high_bands_data': high_bands_data,
         'all_calls': sorted([l['callsign'] for l in persisted_logs]),
         'multipliers': sorted_mults,
+        'is_solo': (log_count == 1),
     }
     return render(request, 'analyzer/multiplier_dashboard.html', context)
 
@@ -1691,15 +1699,18 @@
     # 2. Re-construct Callsigns from the combo_id
     callsigns_safe = combo_id.split('_')
     callsigns_display = [c.upper() for c in callsigns_safe]
+    is_solo = (len(callsigns_safe) == 1)
     
     # 3. Identify Pairs for Strategy Tab
-    import itertools
-    pairs = list(itertools.combinations(callsigns_safe, 2))
     matchups = []
-    for p in pairs:
-        c1, c2 = sorted(p)
-        label = f"{c1.upper()} vs {c2.upper()}"
-        base_path = report_rel_path
-        
-        matchups.append({
-            'label': label,
-            'id': f"{c1}_{c2}",
-            'qso_breakdown_file': os.path.join(base_path, f"charts/qso_breakdown_chart_{c1}_{c2}.html"),
-            'diff_plot_file': os.path.join(base_path, f"plots/cumulative_difference_plots_qsos_all_{c1}_{c2}.html"),
-            'band_activity_file': os.path.join(base_path, f"plots/comparative_band_activity_{c1}_{c2}.html"),
-            'continent_file': os.path.join(base_path, f"text/comparative_continent_summary_{c1}_{c2}.txt")
-        })
+    if not is_solo:
+        import itertools
+        pairs = list(itertools.combinations(callsigns_safe, 2))
+        for p in pairs:
+            c1, c2 = sorted(p)
+            label = f"{c1.upper()} vs {c2.upper()}"
+            base_path = report_rel_path
+            
+            matchups.append({
+                'label': label,
+                'id': f"{c1}_{c2}",
+                'qso_breakdown_file': os.path.join(base_path, f"charts/qso_breakdown_chart_{c1}_{c2}.html"),
+                'diff_plot_file': os.path.join(base_path, f"plots/cumulative_difference_plots_qsos_all_{c1}_{c2}.html"),
+                'band_activity_file': os.path.join(base_path, f"plots/comparative_band_activity_{c1}_{c2}.html"),
+                'continent_file': os.path.join(base_path, f"text/comparative_continent_summary_{c1}_{c2}.txt")
+            })
 
     context = {
         'session_id': session_id,
@@ -1709,6 +1720,8 @@
         'global_qso_rate_file': os.path.join(report_rel_path, f"plots/qso_rate_plots_all_{combo_id}.html"),
         'global_point_rate_file': os.path.join(report_rel_path, f"plots/point_rate_plots_all_{combo_id}.html"),
         'rate_sheet_comparison': os.path.join(report_rel_path, f"text/rate_sheet_comparison_{'_'.join(sorted(callsigns_safe))}.txt"),
-        'report_base': os.path.join(report_rel_path) # Pass base path for template filters
+        'correlation_file': os.path.join(report_rel_path, f"plots/plot_correlation_analysis_{combo_id}.html"),
+        'report_base': os.path.join(report_rel_path), # Pass base path for template filters
+        'is_solo': is_solo
     }
     
     return render(request, 'analyzer/qso_dashboard.html', context)

--- web_app/analyzer/templates/analyzer/qso_dashboard.html
+++ web_app/analyzer/templates/analyzer/qso_dashboard.html
@@ -1823,11 +1823,17 @@
 
     <ul class="nav nav-tabs mb-3" id="qsoTabs" role="tablist">
+        <li class="nav-item" role="presentation">
+            <button class="nav-link {% if is_solo %}active{% endif %}" id="correlations-tab" data-bs-toggle="tab" data-bs-target="#correlations" type="button" role="tab">
+                <i class="bi bi-diagram-2 me-2"></i>Correlations
+            </button>
+        </li>
+        {% if not is_solo %}
         <li class="nav-item" role="presentation">
             <button class="nav-link active" id="strategy-tab" data-bs-toggle="tab" data-bs-target="#strategy" type="button" role="tab">
                 <i class="bi bi-chess me-2"></i>Pairwise Strategy
             </button>
         </li>
+        {% endif %}
         <li class="nav-item" role="presentation">
-            <button class="nav-link" id="rates-tab" data-bs-toggle="tab" data-bs-target="#rates" type="button" role="tab">
+            <button class="nav-link" id="rates-tab" data-bs-toggle="tab" data-bs-target="#rates" type="button" role="tab">
                 <i class="bi bi-table me-2"></i>Rate Detail
             </button>
         </li>
@@ -1837,6 +1843,19 @@
 
     <div class="tab-content" id="qsoTabsContent">
         
+        <div class="tab-pane fade {% if is_solo %}show active{% endif %}" id="correlations" role="tabpanel">
+            <div class="card shadow-sm">
+                <div class="card-header d-flex justify-content-between align-items-center">
+                    <span>Run Traction & Multiplier Yield</span>
+                    <a href="{% url 'view_report' session_id correlation_file %}?source=qso" target="_blank" class="btn btn-xs btn-link text-muted"><i class="bi bi-box-arrow-up-right"></i></a>
+                </div>
+                <div class="card-body p-0" style="height: 900px;">
+                    <iframe src="{% url 'view_report' session_id correlation_file %}?chromeless=1" style="width: 100%; height: 100%; border: none;"></iframe>
+                </div>
+            </div>
+        </div>
+
+        {% if not is_solo %}
         <div class="tab-pane fade show active" id="strategy" role="tabpanel">
             <div class="btn-group mb-3" role="group">
                 {% for m in matchups %}
@@ -1858,8 +1877,9 @@
                 </div>
             </div>
         </div>
+        {% endif %}
 
-        <div class="tab-pane fade" id="rates" role="tabpanel">
+        <div class="tab-pane fade" id="rates" role="tabpanel">
             <div class="btn-group mb-3" role="group">
                 <button type="button" class="btn btn-outline-secondary rate-btn active" 
                         data-src="{% url 'view_report' session_id rate_sheet_comparison %}?chromeless=1"

--- web_app/analyzer/templates/analyzer/multiplier_dashboard.html
+++ web_app/analyzer/templates/analyzer/multiplier_dashboard.html
@@ -1816,7 +1816,11 @@
     </div>
 
-    <h5 class="fw-bold text-secondary mb-3"><i class="bi bi-file-text me-2"></i>Missed Multiplier Reports</h5>
+    {% if is_solo %}
+    <h5 class="fw-bold text-secondary mb-3"><i class="bi bi-file-text me-2"></i>Multiplier Matrix Reports</h5>
+    {% else %}
+    <h5 class="fw-bold text-secondary mb-3"><i class="bi bi-file-text me-2"></i>Missed Multiplier Reports</h5>
+    {% endif %}
     <div class="row row-cols-1 row-cols-md-2 row-cols-xl-4 g-4">
         {% for mult in multipliers %}
             {% if mult.missed %}
             <div class="col">
                 <div class="card h-100 shadow-sm border-0">
                     <div class="card-header bg-white d-flex justify-content-between align-items-center">
-                        <span class="fw-bold text-danger">{{ mult.label }}</span>
+                        <span class="fw-bold {% if is_solo %}text-info{% else %}text-danger{% endif %}">{{ mult.label }}</span>
                         <a href="{% url 'view_report' session_id mult.missed %}?source=mult" target="_blank" class="btn btn-sm btn-link text-muted p-0" title="Full Screen">
                             <i class="bi bi-box-arrow-up-right"></i>
--- END DIFF ---

## 4. Affected Modules Checklist
* `contest_tools/reports/plot_correlation_analysis.py` (New report logic)
* `web_app/analyzer/views.py` (Solo mode detection and report mapping)
* `web_app/analyzer/templates/analyzer/qso_dashboard.html` (UI logic to hide strategy tab and show correlations)
* `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` (UI logic to re-style multiplier cards)

## 5. Pre-Flight Check
* **Inputs:** `session_id`, `log_count` (derived).
* **Expected Outcome:**
    * **Solo Mode (1 Log):**
        * QSO Dashboard: Shows "Correlations" tab (Active), "Rate Detail", "Points". Hides "Strategy".
        * Multiplier Dashboard: Shows "Multiplier Matrix" (Blue) pointing to `multiplier_summary`.
    * **Multi Mode (2+ Logs):**
        * QSO Dashboard: Shows "Correlations" tab (New, but not active), "Strategy" (Active), etc.
        * Multiplier Dashboard: Shows "Missed Multipliers" (Red).
* **Refactoring Impact Analysis:** Low. Changes are purely presentational logic in Views/Templates and additive in Reports.