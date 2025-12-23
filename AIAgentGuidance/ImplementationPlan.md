# ImplementationPlan.md

**Version:** 1.6.0
**Target:** 0.137.1-Beta

## 1. File Identification: web_app/analyzer/templates/analyzer/multiplier_dashboard.html
**Version:** 0.137.0-Beta

### Surgical Changes
1.  **Update "View Text Report" Link**: Append `?source=mult` to the `href` attribute in the "Multiplier Breakdown (Group Par)" card header.
2.  **Update "Full Screen (HTML)" Link**: Append `?source=mult` to the `href` attribute in the "Multiplier Breakdown (Group Par)" card header.

### Surgical Change Verification (diff)
__CODE_BLOCK__ html
--- BEGIN DIFF ---
@@ -18,10 +18,10 @@
             <span class="fw-bold text-secondary"><i class="bi bi-grid-3x3-gap me-2"></i>Multiplier Breakdown (Group Par)</span>
             <div>
                 {% if breakdown_txt_url %}
-                <a href="{% url 'view_report' session_id breakdown_txt_url %}" target="_blank" class="btn btn-sm btn-link text-muted p-0 me-2" title="View Text Report">
+                <a href="{% url 'view_report' session_id breakdown_txt_url %}?source=mult" target="_blank" class="btn btn-sm btn-link text-muted p-0 me-2" title="View Text Report">
                     <i class="bi bi-file-text"></i>
                 </a>
                 {% endif %}
                 {% if breakdown_html_url %}
-                <a href="{% url 'view_report' session_id breakdown_html_url %}" target="_blank" class="btn btn-sm btn-link text-secondary p-0" title="Full Screen (HTML)">
+                <a href="{% url 'view_report' session_id breakdown_html_url %}?source=mult" target="_blank" class="btn btn-sm btn-link text-secondary p-0" title="Full Screen (HTML)">
                     <i class="bi bi-box-arrow-up-right"></i>
                 </a>
                 {% endif %}
--- END DIFF ---
__CODE_BLOCK__

## 2. Pre-Flight Check
* **Inputs**: `manifest_bundle.txt`.
* **Expected Outcome**:
    * Clicking the Text or HTML icon in the top card of the Multiplier Dashboard will pass `source=mult` to the report viewer.
    * The "Back" button on the report viewer will correctly return to the Multiplier Dashboard instead of the Main Dashboard.
* **Mental Walkthrough**:
    1.  User navigates to Multiplier Dashboard.
    2.  User clicks the Text Report icon in the top header.
    3.  Report Viewer loads.
    4.  User clicks "Back to Multiplier Dashboard".
    5.  User is returned to the correct screen.
* **State Confirmation**: I will request `Confirmed` before delivery.