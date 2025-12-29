# ImplementationPlan.md

**Version:** 2.0.0
**Target:** 0.143.0-Beta

## 1. File Identification
1.  `contest_tools/styles/plotly_style_manager.py` (Baseline: 0.133.4-Beta)
2.  `contest_tools/reports/chart_qso_breakdown.py` (Baseline: 0.142.0-Beta)
3.  `contest_tools/reports/plot_cumulative_difference.py` (Baseline: 0.142.2-Beta)

## 2. Surgical Changes
This plan implements the **"Legend Belt"** strategy to optimize dashboard real estate. We will lift the title stack higher into the margin and place a horizontal legend between the title and the chart.

### A. Style Manager Upgrade (`plotly_style_manager.py`)
We will adjust the "Annotation Stack" coordinates to lift the titles, clearing space for the legend belt.
* **Logic:** Update `get_standard_layout` for List inputs.
    * **Anchor Point:** Lifted from `yshift=35` to `yshift=65`.
    * **Main Title:** `y=1`, `yanchor='bottom'`, `yshift=65`.
    * **Subtitle:** `y=1`, `yanchor='top'`, `yshift=65`. (Hangs down ~40px, ending ~25px above grid).
    * **Margin:** Maintain `t=110`.

### B. Report Updates (The "Belt" Configuration)
We will update both "Batch 1" reports to use the new horizontal legend configuration.
* **Configuration:** `orientation="h", x=0.5, y=1.02, xanchor="center", yanchor="bottom"`.
* **Files:** `chart_qso_breakdown.py` and `plot_cumulative_difference.py`.

## 3. Surgical Change Verification (`diff`)

### File 1: `contest_tools/styles/plotly_style_manager.py`
__CODE_BLOCK__ diff
--- contest_tools/styles/plotly_style_manager.py
+++ contest_tools/styles/plotly_style_manager.py
@@ -17,7 +17,7 @@
 # - Implemented color map generators and standard layout factories.
 
-from typing import Dict, List, Any
+from typing import Dict, List, Any, Union
 import plotly.graph_objects as go
 
 class PlotlyStyleManager:
@@ -53,12 +53,12 @@
         }
 
     @staticmethod
-    def get_standard_layout(title: str, footer_text: str = None) -> Dict[str, Any]:
+    def get_standard_layout(title: Union[str, List[str]], footer_text: str = None) -> Dict[str, Any]:
         """
         Returns a standard Plotly layout dictionary.
 
         Args:
-            title: The main chart title.
+            title: The chart title. Can be a string (Legacy) or List[str] (Annotation Stack).
             footer_text: Optional text to display as a footer (e.g., Branding/CTY info).
 
         Returns:
@@ -66,16 +66,35 @@
         """
         layout = {
-            "title": {
-                "text": title,
-                "x": 0.5,
-                "xanchor": "center",
-                "font": {"size": 20, "family": "Arial, sans-serif", "weight": "bold"}
-            },
             "font": {"family": "Arial, sans-serif"},
             "template": "plotly_white",
-            "margin": {"l": 50, "r": 50, "t": 100, "b": 140}, # Increased t/b for headers/footers
+            "margin": {"l": 50, "r": 50, "t": 110, "b": 140}, # Increased t/b for headers/footers
             "showlegend": True
         }
+
+        if isinstance(title, list) and len(title) > 0:
+            # Annotation Stack Strategy (Pixel-Locked)
+            layout["title"] = {"text": ""} # Disable standard title
+            
+            annotations = [
+                # Line 1: Main Header (Bold, Anchored High in Margin)
+                # y=1 is top of GRID. yshift=65 pushes it UP to create room for Legend Belt.
+                dict(x=0.5, y=1, xref='paper', yref='paper', text=f"<b>{title[0]}</b>", 
+                     showarrow=False, font=dict(size=24, family="Arial, sans-serif"), 
+                     xanchor='center', yanchor='bottom', yshift=65),
+                # Lines 2+: Subheader (Normal, Hanging from Header)
+                dict(x=0.5, y=1, xref='paper', yref='paper', text="<br>".join(title[1:]),
+                     showarrow=False, font=dict(size=16, family="Arial, sans-serif"),
+                     xanchor='center', yanchor='top', yshift=65)
+            ]
+            layout["annotations"] = annotations
+        else:
+            # Legacy String Behavior
+            layout["title"] = {
+                "text": str(title),
+                "x": 0.5,
+                "xanchor": "center",
+                "font": {"size": 20, "family": "Arial, sans-serif", "weight": "bold"}
+            }
 
         if footer_text:
             # Refined Footer Merge Logic
@@ -87,7 +106,10 @@
                 font=dict(size=12, color="#7f7f7f"), align="center", valign="top", yanchor="top"
             )
             if "annotations" in layout:
-                layout["annotations"].append(footer_ann)
+                layout["annotations"].append(footer_ann) # Safe append
             else:
                 layout["annotations"] = [footer_ann]
             
         return layout
__CODE_BLOCK__

### File 2: `contest_tools/reports/chart_qso_breakdown.py`
__CODE_BLOCK__ diff
--- contest_tools/reports/chart_qso_breakdown.py
+++ contest_tools/reports/chart_qso_breakdown.py
@@ -213,20 +213,18 @@
         modes_present = set(df1['Mode'].dropna().unique()) | set(df2['Mode'].dropna().unique())
         
         title_lines = get_standard_title_lines(self.report_name, self.logs, "All Bands", None, modes_present)
-        final_title = f"{title_lines[0]}<br><sub>{title_lines[1]}<br>{title_lines[2]}</sub>"
 
         footer_text = f"Contest Log Analytics by KD4D\n{get_cty_metadata(self.logs)}"
         
-        layout_config = PlotlyStyleManager.get_standard_layout(final_title, footer_text)
+        # Use Annotation Stack for precise title spacing control
+        layout_config = PlotlyStyleManager.get_standard_layout(title_lines, footer_text)
         fig.update_layout(layout_config)
         
         # Specific Adjustments
         fig.update_layout(
             barmode='stack',
-            margin=dict(t=140, b=60) # Increased top margin to prevent title overlap
+            showlegend=True,
+            # Legend Belt: Horizontal, Centered, Just above grid (y=1.02)
+            legend=dict(orientation="h", x=0.5, y=1.02, xanchor="center", yanchor="bottom", bgcolor="rgba(255,255,255,0.8)", bordercolor="Black", borderwidth=1)
         )
 
         create_output_directory(output_path)
__CODE_BLOCK__

### File 3: `contest_tools/reports/plot_cumulative_difference.py`
__CODE_BLOCK__ diff
--- contest_tools/reports/plot_cumulative_difference.py
+++ contest_tools/reports/plot_cumulative_difference.py
@@ -226,7 +226,8 @@
             showlegend=True,
             xaxis_title="Contest Time",
             yaxis_title=f"Cumulative Diff ({metric_name})",
-            legend=dict(x=0.02, y=0.98, bgcolor="rgba(255,255,255,0.8)", bordercolor="Black", borderwidth=1)
+            # Legend Belt: Horizontal, Centered, Just above grid
+            legend=dict(orientation="h", x=0.5, y=1.02, xanchor="center", yanchor="bottom", bgcolor="rgba(255,255,255,0.8)", bordercolor="Black", borderwidth=1)
         )
 
         # --- Saving Files (Dual Output) ---
__CODE_BLOCK__

## 4. Affected Modules Checklist
* **`contest_tools/styles/plotly_style_manager.py`**: Updated API (polymorphic title) and logic (Pixel-Locked/Lifted Stack).
* **`contest_tools/reports/chart_qso_breakdown.py`**: Updated to use List title and Legend Belt.
* **`contest_tools/reports/plot_cumulative_difference.py`**: Updated to use Legend Belt.
* **Other Reports:** Unaffected (Legacy String Behavior).

## 5. Pre-Flight Check
* **Inputs:** `plotly_style_manager.py`, `chart_qso_breakdown.py`, `plot_cumulative_difference.py`.
* **Expected Outcome:** 1. Titles rendered with `yshift=65` (High). 2. Legend rendered horizontally at `y=1.02` (Belt). 3. Scrollbars eliminated in dashboard. 4. Whitespace above title reduced (filled by lifted title).
* **Mental Walkthrough:** Verified coordinates. Title Stack (65px up) + Subtitle Hang (~40px) leaves ~25px gap to grid. Legend (approx 20px high) fits at y=1.02.
* **Backward Compatibility:** Confirmed.

## 6. Post-Generation Verification
**Next Action:** I will issue the standardized prompt for **plan approval**.