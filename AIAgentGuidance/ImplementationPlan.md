**Version:** 1.0.0
**Target:** 0.127.2-Beta

# Implementation Plan - The Inline Scorecard Refactoring

## User Story
As an Architect, I want to optimize the visual density of the Multiplier Breakdown table by moving the red "missed" delta numbers inline with the total counts (e.g., `99 (-5)`) and spelling out the column headers, so that the report is more readable and requires less vertical scrolling.

## Technical Approach
1.  **Template Refactoring (`breakdown_rows.html`):**
    * Replace the block-level `div` structure for station stats with a single inline format.
    * Enforce the pattern: `{{ count }} <span class="text-danger">({{ delta }})</span>`.
    * Hardcode the delta color to `text-danger` as requested.
    * Add `text-nowrap` to the table cell to strictly enforce the inline requirement on smaller screens.
2.  **Header Expansion (`multiplier_dashboard.html`):**
    * Locate the "Low Bands" and "High Bands" table headers.
    * Replace abbreviations `Wrkd` -> `Worked` and `Com` -> `Common`.

## Affected Files
1.  `web_app/analyzer/templates/analyzer/partials/breakdown_rows.html`
2.  `web_app/analyzer/templates/analyzer/multiplier_dashboard.html`

## Surgical Changes

### 1. `web_app/analyzer/templates/analyzer/partials/breakdown_rows.html`
* **Change:** Convert stacked divs to inline span with hardcoded red color and parentheses.

__CODE_BLOCK__html
<<<<
    {% for stat in row.stations %}
    <td>
        <div>{{ stat.count }}</div>
        {% if stat.delta != 0 %}
        <div class="small {% if stat.delta > 0 %}text-success{% else %}text-danger{% endif %}" style="font-size: 0.75rem;">
            {{ stat.delta|stringformat:"+d" }}
        </div>
        {% endif %}
    </td>
    {% endfor %}
====
    {% for stat in row.stations %}
    <td class="text-nowrap">
        {{ stat.count }}
        {% if stat.delta != 0 %}
        <span class="text-danger">({{ stat.delta|stringformat:"+d" }})</span>
        {% endif %}
    </td>
    {% endfor %}
>>>>
__CODE_BLOCK__

### 2. `web_app/analyzer/templates/analyzer/multiplier_dashboard.html`
* **Change:** Expand headers for "Low Bands" section.

__CODE_BLOCK__html
<<<<
                                    <tr>
                                        <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
                                        <th>Wrkd</th>
                                        <th>Com</th>
                                        {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                    </tr>
====
                                    <tr>
                                        <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
                                        <th>Worked</th>
                                        <th>Common</th>
                                        {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                    </tr>
>>>>
__CODE_BLOCK__

* **Change:** Expand headers for "High Bands" section.

__CODE_BLOCK__html
<<<<
                                    <tr>
                                        <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
                                        <th>Wrkd</th>
                                        <th>Com</th>
                                        {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                    </tr>
====
                                    <tr>
                                        <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
                                        <th>Worked</th>
                                        <th>Common</th>
                                        {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                    </tr>
>>>>
__CODE_BLOCK__

## Surgical Change Verification (Diff)

__CODE_BLOCK__text
--- BEGIN DIFF ---
--- web_app/analyzer/templates/analyzer/partials/breakdown_rows.html
+++ web_app/analyzer/templates/analyzer/partials/breakdown_rows.html
@@ -7,12 +7,9 @@
     <td>{{ row.common }}</td>
     {% for stat in row.stations %}
-    <td>
-        <div>{{ stat.count }}</div>
+    <td class="text-nowrap">
+        {{ stat.count }}
         {% if stat.delta != 0 %}
-        <div class="small {% if stat.delta > 0 %}text-success{% else %}text-danger{% endif %}" style="font-size: 0.75rem;">
-            {{ stat.delta|stringformat:"+d" }}
-        </div>
+        <span class="text-danger">({{ stat.delta|stringformat:"+d" }})</span>
         {% endif %}
     </td>
     {% endfor %}

--- web_app/analyzer/templates/analyzer/multiplier_dashboard.html
+++ web_app/analyzer/templates/analyzer/multiplier_dashboard.html
@@ -48,8 +48,8 @@
                                     <tr>
                                         <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
-                                        <th>Wrkd</th>
-                                        <th>Com</th>
+                                        <th>Worked</th>
+                                        <th>Common</th>
                                         {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                     </tr>
                                 </thead>
@@ -64,8 +64,8 @@
                                     <tr>
                                         <th class="text-start ps-2" style="width: 20%;">{{ block.label }}</th>
-                                        <th>Wrkd</th>
-                                        <th>Com</th>
+                                        <th>Worked</th>
+                                        <th>Common</th>
                                         {% for call in all_calls %}<th>{{ call }}</th>{% endfor %}
                                     </tr>
                                 </thead>
--- END DIFF ---
__CODE_BLOCK__

## Pre-Flight Check
1.  **Inputs:** `breakdown_rows.html`, `multiplier_dashboard.html`.
2.  **Outcome:** The Multiplier Breakdown table will display compact rows. The redundant vertical space from the stacked divs will be eliminated. Headers will be fully readable.
3.  **Visual Confirmation:**
    * **Old:** `99` (newline) `-5` (small font)
    * **New:** `99 (-5)` (base font, red)
4.  **Impact Analysis:** Changes are restricted to template HTML. No impact on data aggregation logic or Python code.