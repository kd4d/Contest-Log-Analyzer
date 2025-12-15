# ImplementationPlan.md

**Version:** 1.0.0
**Target:** 0.117.0-Beta

## 1. File: `contest_tools/reports/plot_point_rate.py`
**Version:** 0.113.3-Beta (Baseline)

### Surgical Changes
I will update the `fig.update_layout` call responsible for the specific layout overrides to move the legend from the top-right (external) to the top-left (internal), matching the behavior of the QSO Rate Plot.

* **Change 1:** In `_create_plot`, modify the `legend` dictionary within `fig.update_layout` from `dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)` to `dict(x=0.01, y=0.99)`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -233,3 +233,3 @@
             xaxis_title="Contest Time",
             yaxis_title=f"Cumulative {metric_name}",
-            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
+            legend=dict(x=0.01, y=0.99)
         )
--- END DIFF ---

---

## 2. File: `contest_tools/reports/plot_qso_rate.py`
**Version:** 0.113.3-Beta (Baseline)

### Surgical Changes
I will update the `go.Table` definition in `_create_plot` to match the "grid style" used in the Point Rate Plot.

* **Change 1:** In `go.Table` -> `header`, change `fill_color` from `'paleturquoise'` to `"#f0f0f0"` and add `line_color="darkgray"`.
* **Change 2:** In `go.Table` -> `cells`, add `line_color="lightgray"`.

### Surgical Change Verification (`diff`)
--- BEGIN DIFF ---
@@ -262,7 +262,7 @@
                 header=dict(
                     values=headers,
-                    fill_color='paleturquoise',
+                    fill_color="#f0f0f0",
+                    line_color="darkgray",
                     align='center',
                     font=dict(size=12, weight='bold')
                 ),
                 cells=dict(
@@ -270,4 +270,5 @@
                     fill_color='white',
+                    line_color="lightgray",
                     align='center',
                     font=dict(size=11),
                     height=30
--- END DIFF ---

---

## 3. Affected Modules Checklist
* **Protocol 7.6 (Systemic Bug Eradication):** I have reviewed other chart reports. `plot_cumulative_difference.py` and `plot_comparative_band_activity.py` use `showlegend=True` with default positioning or specific horizontal layouts appropriate for their data density. Only these two "Rate Comparison" plots share the specific `XY Plot + Table` layout that benefits from this alignment. No other modules require changes.

## 4. Pre-Flight Check
* **Inputs:**
    * `contest_tools/reports/plot_point_rate.py` (v0.113.3-Beta)
    * `contest_tools/reports/plot_qso_rate.py` (v0.113.3-Beta)
* **Expected Outcome:**
    * The Point Rate Plot legend will appear in the top-left corner, avoiding cutoff.
    * The QSO Rate Plot table will have distinct grid lines and a gray header, matching the Point Rate Plot table.
* **Mental Walkthrough:**
    * `plot_point_rate`: The `update_layout` call is near line 233. The dictionary key is `legend`. I will replace the complex anchor logic with simple x/y coordinates.
    * `plot_qso_rate`: The `go.Table` is near line 258. I will inject the `line_color` attributes into the `header` and `cells` dictionaries.
* **Visual Compliance:** Explicitly verified adherence to the user's styling preference.