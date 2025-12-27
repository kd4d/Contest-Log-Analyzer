**Version:** 1.0.0
**Target:** 0.142.0-Beta

# Implementation Plan - Fix QSO Breakdown Chart Layout Overlap

## 1. File Identification
* **File:** `contest_tools/reports/chart_qso_breakdown.py`
* **Baseline Version:** 0.141.0-Beta

## 2. Surgical Changes
I will modify the Plotly layout configuration to resolve the overlap between the X-axis labels (Band Name) and the subsequent rows of subplots.

1.  **Increase Vertical Spacing:** In the `make_subplots` initialization, I will increase `vertical_spacing` from `0.05` to `0.15`. This reserves significantly more vertical screen real estate between the rows of charts, preventing the axis title of Row 1 from colliding with the chart title/bars of Row 2.
2.  **Tighten Axis Labels:** Inside the band loop, I will update the `fig.update_xaxes` call to include `title_standoff=5`. This reduces the default gap between the tick labels ("Call", "Common") and the axis title ("160M"), visually grouping them tighter together as requested ("single spacing").
3.  **Adjust Global Margins:** I will update the `fig.update_layout` calls (both the global one and the HTML-specific override) to explicitly set `b=60` (Bottom Margin). This ensures the labels on the final row are not cut off by the canvas edge.

## 3. Surgical Change Verification (`diff`)
```text
--- BEGIN DIFF ---
--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -19,6 +19,10 @@
 #
 # --- Revision History ---
+# [0.142.0-Beta] - 2025-12-27
+# - Increased subplot vertical_spacing to 0.15 to prevent label overlap.
+# - Reduced X-axis title_standoff to 5 to tighten Band Label placement.
+# - Increased bottom margin to 60px to accommodate labels.
 # [0.141.0-Beta] - 2025-12-25
 # - Removed floating subplot titles to eliminate overlap.
 # - Added x-axis titles to subplots for clearer band identification.
@@ -107,7 +111,7 @@
             rows=rows, 
             cols=cols, 
             shared_yaxes=True,
-            vertical_spacing=0.05
+            vertical_spacing=0.15
         )
 
         colors = PlotlyStyleManager.get_qso_mode_colors()
@@ -129,7 +133,7 @@
                     ),
                     row=row, col=col
                 )
-            fig.update_xaxes(title_text=band, row=row, col=col)
+            fig.update_xaxes(title_text=band, title_standoff=5, row=row, col=col)
 
         # Standard Layout Application
         modes_present = set(df1['Mode'].dropna().unique()) | set(df2['Mode'].dropna().unique())
@@ -144,7 +148,7 @@
         # Specific Adjustments
         fig.update_layout(
             barmode='stack',
-            margin=dict(t=140) # Increased top margin to prevent title overlap
+            margin=dict(t=140, b=60) # Increased top margin to prevent title overlap
         )
 
         create_output_directory(output_path)
@@ -176,7 +180,7 @@
         fig.layout.width = None
         
         # Optimize margins for dashboard display
-        fig.update_layout(margin=dict(t=100, b=40, l=50, r=50))
+        fig.update_layout(margin=dict(t=100, b=60, l=50, r=50))
         
         config = {
             'toImageButtonOptions': {'filename': base_filename, 'format': 'png'},
--- END DIFF ---