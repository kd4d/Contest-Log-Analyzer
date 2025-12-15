# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.118.0-Beta

## 1. File: `web_app/analyzer/templates/analyzer/report_viewer.html`
**Version:** 0.115.0-Beta (Baseline)

### Surgical Changes
I will add a "Download" button to the report viewer toolbar. This button uses the HTML5 `download` attribute to trigger the browser's save dialog (or auto-save), utilizing the provided descriptive filename.

* **Change 1:** Inside the toolbar `div`, immediately after the "Back" button, insert the new "Download" button anchor tag.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -7,4 +7,5 @@
         <a href="{{ back_url }}" class="btn btn-sm btn-outline-secondary">
             <i class="bi bi-arrow-left me-1"></i>{{ back_label }}
         </a>
+        <a href="{{ iframe_src }}" download="{{ filename }}" class="btn btn-sm btn-outline-primary ms-2">
+            <i class="bi bi-download me-1"></i>Download
+        </a>
     </div>
--- END DIFF ---

---

## 2. File: `contest_tools/reports/plot_qso_rate.py`
**Version:** 0.113.3-Beta (Baseline)

### Surgical Changes
I will inject the Plotly configuration object into the `write_html` call to ensure the "Camera" icon downloads a file with the correct descriptive name instead of `newplot.png`.

* **Change 1:** In `_create_plot`, define the `config` dictionary using `base_filename`.
* **Change 2:** Pass `config=config` to `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -253,3 +253,5 @@
             width=None,
             height=None
         )
-        fig.write_html(html_path, include_plotlyjs='cdn')
+        
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
         
         # 2. PNG (Static) - Return this path for consistency with report list
--- END DIFF ---

---

## 3. File: `contest_tools/reports/plot_point_rate.py`
**Version:** 0.113.3-Beta (Baseline)

### Surgical Changes
Similar to `plot_qso_rate.py`, I will inject the filename configuration for the interactive HTML export.

* **Change 1:** In `_create_plot`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -232,3 +232,5 @@
             width=None,
             height=None
         )
-        fig.write_html(html_path, include_plotlyjs='cdn')
+
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_path, include_plotlyjs='cdn', config=config)
         
         # Save PNG (Static)
--- END DIFF ---

---

## 4. File: `contest_tools/reports/plot_cumulative_difference.py`
**Version:** 0.115.0-Beta (Baseline)

### Surgical Changes
Apply the configuration injection to the cumulative difference plot generator.

* **Change 1:** In `_generate_single_plot`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -124,3 +124,5 @@
                 height=None
             )
-            fig.write_html(html_path, include_plotlyjs='cdn')
+            
+            config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+            fig.write_html(html_path, include_plotlyjs='cdn', config=config)
             generated_files.append(html_path)
--- END DIFF ---

---

## 5. File: `contest_tools/reports/chart_qso_breakdown.py`
**Version:** 0.115.2-Beta (Baseline)

### Surgical Changes
Apply configuration injection to the QSO Breakdown chart.

* **Change 1:** In `generate`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -140,3 +140,5 @@
             height=None
         )
-        fig.write_html(html_file, include_plotlyjs='cdn')
+        
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_file, include_plotlyjs='cdn', config=config)
 
         # Return list of successfully created files (checking existence)
--- END DIFF ---

---

## 6. File: `contest_tools/reports/plot_comparative_band_activity.py`
**Version:** 0.114.0-Beta (Baseline)

### Surgical Changes
Apply configuration injection. Note that this file uses `filename_base` variable name instead of `base_filename`.

* **Change 1:** In `_generate_plot_for_slice`, define `config` using `filename_base`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -163,3 +163,5 @@
             # Save HTML
-            fig.write_html(filepath_html, include_plotlyjs='cdn')
+            
+            config = {'toImageButtonOptions': {'filename': filename_base, 'format': 'png'}}
+            fig.write_html(filepath_html, include_plotlyjs='cdn', config=config)
             results.append(f"Interactive plot saved: {filepath_html}")
             
--- END DIFF ---

---

## 7. File: `contest_tools/reports/plot_comparative_run_sp.py`
**Version:** 1.2.0 (Baseline)

### Surgical Changes
Apply configuration injection. Uses `base_filename`.

* **Change 1:** In `_generate_plot_for_page`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -190,3 +190,5 @@
         save_debug_data(debug_data_flag, output_path, plot_data_for_debug, custom_filename=debug_filename)
         
-        fig.write_html(html_path)
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_path, config=config)
         fig.write_image(png_path)
         
--- END DIFF ---

---

## 8. File: `contest_tools/reports/chart_point_contribution.py`
**Version:** 1.0.0 (Baseline)

### Surgical Changes
Apply configuration injection. Uses `base_filename`.

* **Change 1:** In `generate`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -116,3 +116,5 @@
 
         # Save HTML (New Interactive Requirement)
-        fig.write_html(html_file, include_plotlyjs='cdn')
+        
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_file, include_plotlyjs='cdn', config=config)
         generated_files.append(html_file)
 
--- END DIFF ---

---

## 9. File: `contest_tools/reports/chart_point_contribution_single.py`
**Version:** 1.0.1 (Baseline)

### Surgical Changes
Apply configuration injection. Uses `base_filename`.

* **Change 1:** In `generate`, define `config` using `base_filename`.
* **Change 2:** Update `fig.write_html`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -118,3 +118,5 @@
         # Save Dual Outputs
         fig.write_image(png_file)
-        fig.write_html(html_file)
+        
+        config = {'toImageButtonOptions': {'filename': base_filename, 'format': 'png'}}
+        fig.write_html(html_file, config=config)
 
         return [png_file, html_file]
--- END DIFF ---

## 10. Pre-Flight Check
* **Inputs:** 9 source files (1 Template, 8 Python Reports).
* **Expected Outcome:**
    * The report viewer will show a "Download" button that triggers a save dialog for text files.
    * All Plotly charts (except the animation, which was already done) will have a Camera icon that saves a PNG with a descriptive filename (e.g., `qso_rate_plots_all_call1_call2.png`) instead of `newplot.png`.
* **Mental Walkthrough:** Verified variable names for each Python file (`base_filename` vs `filename_base`). Verified HTML syntax for the download attribute.
* **Visual Compliance:** N/A (Backend/Template Logic).