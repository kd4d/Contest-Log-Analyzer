**Version:** 1.0.0
**Target:** 0.127.0-Beta

**1. contest_tools/data_aggregators/multiplier_stats.py**
* **Refactor:** Rename `get_dashboard_matrix_data` to `get_multiplier_breakdown_data` to reflect the new hierarchical structure.
* **Logic:** Implement a 3-level aggregation strategy:
    1.  **Grand Total:** Aggregates all multipliers across all bands and rules into a single set per log (using composite keys to respect scoring rules).
    2.  **Band Totals:** Aggregates all multipliers for a specific band across all rules.
    3.  **Rule Totals:** Aggregates specific multiplier types (e.g., Countries) within a band.
* **Dependency:** Utilize `ComparativeEngine` to calculate Union (Total Worked), Common, and Deltas for each level.

**2. web_app/analyzer/views.py**
* **Update:** Modify `multiplier_dashboard` to call the new `get_multiplier_breakdown_data` method.
* **Context:** Rename the template variable from `matrix_data` to `breakdown_rows` to align with the new list-based structure.

**3. web_app/analyzer/templates/analyzer/multiplier_dashboard.html**
* **UI Overhaul:** Replace the "Opportunity Matrix" table with the "Multiplier Breakdown" table.
* **Styling:**
    * Implement hierarchical indentation (Bold for Band/Total lines, indented for specific rules).
    * Add the logic to display `{{ count }} (-{{ delta }})`.
    * Apply `text-danger` class to the delta value.

--- BEGIN DIFF ---
--- contest_tools/data_aggregators/multiplier_stats.py
+++ contest_tools/data_aggregators/multiplier_stats.py
@@ -124,14 +124,14 @@
         return full_results
 
-    def get_dashboard_matrix_data(self) -> Dict[str, Any]:
+    def get_multiplier_breakdown_data(self) -> List[Dict[str, Any]]:
         """
-        Generates high-level metrics for the Dashboard Opportunity Matrix.
-        Returns a dictionary of multiplier types, each containing band-by-band data.
+        Generates hierarchical metrics for the Multiplier Breakdown table.
+        Returns a list of rows (Total -> Band -> Rule) with par/delta metrics.
         """
-        results = {}
         all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in self.logs])
-
+        
+        # 1. Collect all raw multiplier sets
+        # Structure: sets[log_call] = set of items
+        # Items are composite keys: (rule_name, band, value) to ensure uniqueness logic matches scoring
+        
+        raw_sets = {call: set() for call in all_calls}
+        
+        # We also need subsets for aggregations
+        # subset_keys: 'TOTAL', 'TOTAL_{Rule}', '{Band}', '{Band}_{Rule}'
+        subsets = {call: {} for call in all_calls}
+        
+        valid_bands = self.contest_def.valid_bands
+        
         for rule in self.contest_def.multiplier_rules:
             mult_name = rule['name']
             mult_column = rule['value_column']
-            
-            # Process bands
-            bands = self.contest_def.valid_bands + ['All Bands'] if rule.get('totaling_method') == 'sum_of_bands' else ['All Bands']
-            
-            band_rows = []
-            for band in bands:
-                # Build sets for this band
-                mult_sets = {call: set() for call in all_calls}
-                
-                for log in self.logs:
-                    call = log.get_metadata().get('MyCall', 'Unknown')
-                    df = log.get_processed_data()
-                    
-                    if df.empty or mult_column not in df.columns: continue
-                    
-                    df_scope = df if band == "All Bands" else df[df['Band'] == band]
-                    
-                    # Filter valids
-                    valid_mults = df_scope[df_scope[mult_column].notna()]
-                    valid_mults = valid_mults[valid_mults[mult_column] != 'Unknown']
-                    
-                    mult_sets[call].update(valid_mults[mult_column].unique())
-
-                # Compare
-                comp = ComparativeEngine.compare_logs(mult_sets)
-                
-                # Calculate Metrics
-                common_count = comp.common_count
-                union_count = comp.universe_count
-                diff_count = union_count - common_count
-                
-                station_data = {}
-                for call in all_calls:
-                    worked = len(mult_sets[call])
-                    missed_items = sorted(list(comp.station_metrics[call].missed_items)) if call in comp.station_metrics else []
-                    station_data[call] = {'worked': worked, 'missed': len(missed_items), 'missed_items': missed_items}
-
-                band_rows.append({
-                    'name': band,
-                    'common': common_count,
-                    'diff': diff_count,
-                    'stations': station_data
-                })
-
-            results[mult_name] = band_rows
-            
-        return results
+            method = rule.get('totaling_method', 'sum_by_band')
+            
+            for log in self.logs:
+                call = log.get_metadata().get('MyCall', 'Unknown')
+                df = log.get_processed_data()
+                
+                if df.empty or mult_column not in df.columns: continue
+                
+                # Filter valid
+                valid = df[df[mult_column].notna() & (df[mult_column] != 'Unknown')]
+                
+                if method == 'once_per_log':
+                    # Scope: Global. Key: (Rule, Value)
+                    # Just grab unique values
+                    uniques = valid[mult_column].unique()
+                    for val in uniques:
+                        composite_key = (mult_name, 'All', val)
+                        raw_sets[call].add(composite_key)
+                        
+                        # Populate Subsets
+                        # 1. Total
+                        subsets[call].setdefault('TOTAL', set()).add(composite_key)
+                        # 2. Total_Rule
+                        subsets[call].setdefault(f'TOTAL_{mult_name}', set()).add(composite_key)
+                        # No band breakdown for once_per_log in this table
+                        
+                else:
+                    # Scope: Per Band. Key: (Rule, Band, Value)
+                    grouped = valid.groupby('Band')[mult_column].unique()
+                    for band, values in grouped.items():
+                        for val in values:
+                            composite_key = (mult_name, band, val)
+                            raw_sets[call].add(composite_key)
+                            
+                            # Populate Subsets
+                            # 1. Total (Global Score Sum)
+                            subsets[call].setdefault('TOTAL', set()).add(composite_key)
+                            # 2. Total_Rule (Global Rule Sum)
+                            subsets[call].setdefault(f'TOTAL_{mult_name}', set()).add(composite_key)
+                            # 3. Band Total (Sum of all rules on this band)
+                            subsets[call].setdefault(band, set()).add(composite_key)
+                            # 4. Band_Rule (Specific)
+                            subsets[call].setdefault(f'{band}_{mult_name}', set()).add(composite_key)
+
+        # 2. Helper to run comparison and build row
+        def build_row(label, set_key, indent=0, is_bold=False):
+            # Build dictionary of sets for this specific key across all logs
+            sets_to_compare = {}
+            for call in all_calls:
+                sets_to_compare[call] = subsets[call].get(set_key, set())
+            
+            comp = ComparativeEngine.compare_logs(sets_to_compare)
+            
+            stations_data = {}
+            for call in all_calls:
+                metrics = comp.station_metrics.get(call)
+                if metrics:
+                    stations_data[call] = {
+                        'count': metrics.count,
+                        'delta': metrics.count - comp.universe_count # Delta from Par (Total Worked)
+                    }
+                else:
+                    stations_data[call] = {'count': 0, 'delta': -comp.universe_count}
+
+            return {
+                'label': label,
+                'indent': indent,
+                'is_bold': is_bold,
+                'total_worked': comp.universe_count,
+                'common': comp.common_count,
+                'stations': stations_data
+            }
+
+        rows = []
+        
+        # 3. Build Table Rows
+        # A. Grand Total
+        rows.append(build_row("TOTAL", "TOTAL", indent=0, is_bold=True))
+        
+        # B. Global Rule Breakdowns
+        for rule in self.contest_def.multiplier_rules:
+            r_name = rule['name']
+            rows.append(build_row(r_name, f"TOTAL_{r_name}", indent=1, is_bold=False))
+            
+        rows.append({'is_spacer': True}) # Spacer for template
+
+        # C. Per Band Breakdowns (only if not once_per_log heavy)
+        # Only show bands if there is data
+        has_band_data = any(len(subsets[c].get(b, set())) > 0 for c in all_calls for b in valid_bands)
+        
+        if has_band_data:
+            for band in valid_bands:
+                # Check if band has activity
+                if not any(len(subsets[c].get(band, set())) > 0 for c in all_calls):
+                    continue
+                    
+                rows.append(build_row(band, band, indent=0, is_bold=True))
+                for rule in self.contest_def.multiplier_rules:
+                    if rule.get('totaling_method') == 'once_per_log': continue
+                    r_name = rule['name']
+                    rows.append(build_row(r_name, f"{band}_{r_name}", indent=1, is_bold=False))
+                
+                rows.append({'is_spacer': True})
+
+        return rows

--- web_app/analyzer/views.py
+++ web_app/analyzer/views.py
@@ -194,7 +194,7 @@
     
     # Aggregate Matrix
     mult_agg = MultiplierStatsAggregator(lm.logs)
-    matrix_data = mult_agg.get_dashboard_matrix_data()
+    breakdown_rows = mult_agg.get_multiplier_breakdown_data()
 
     # Aggregate Scoreboard (Simple scalars)
     # We can reuse TimeSeriesAggregator for consistency or just pull from logs
@@ -237,7 +237,7 @@
         'session_id': session_id,
         'scoreboard': persisted_logs, # Use persisted logs for accurate scores
         'col_width': col_width,
-        'matrix_data': matrix_data,
+        'breakdown_rows': breakdown_rows,
         'all_calls': sorted([l['callsign'] for l in persisted_logs]),
         'multipliers': sorted_mults,
     }

--- web_app/analyzer/templates/analyzer/multiplier_dashboard.html
+++ web_app/analyzer/templates/analyzer/multiplier_dashboard.html
@@ -37,7 +37,7 @@
                 <div class="alert alert-warning small">No multiplier reports found.</div>
                 {% endfor %}
             </div>
         </div>
 
         <div class="col-md-9 col-lg-10">
             <div class="tab-content" id="v-pills-tabContent">
-                {% for mult in multipliers %}
-                <div class="tab-pane fade {% if forloop.first %}show active{% endif %}" id="v-pills-{{ forloop.counter }}" role="tabpanel" aria-labelledby="v-pills-{{ forloop.counter }}-tab">
-                    
-                    <div class="card mb-4">
-                        <div class="card-header fw-bold bg-light">Opportunity Matrix: {{ mult.label }}</div>
-                        <div class="card-body p-0">
-                            <table class="table table-sm table-striped table-hover mb-0 text-center">
-                                <thead class="table-dark">
-                                    <tr>
-                                        <th>Band</th>
-                                        <th>Common</th>
-                                        <th>Diff</th>
-                                        {% for call in all_calls %}
-                                        <th>{{ call }}</th>
-                                        {% endfor %}
-                                    </tr>
-                                </thead>
-                                <tbody>
-                                    {% for mult_name, rows in matrix_data.items %}
-                                        {% if mult_name|lower == mult.label|lower %}
-                                            {% for row in rows %}
-                                            <tr>
-                                                <td class="fw-bold">{{ row.name }}</td>
-                                                <td>{{ row.common }}</td>
-                                                <td>{{ row.diff }}</td>
-                                                {% for call in all_calls %}
-                                                    {% for station_call, data in row.stations.items %}
-                                                        {% if station_call == call %}
-                                                        <td>
-                                                            {{ data.worked }}
-                                                            {% if data.missed > 0 %}
-                                                                <span class="text-danger fw-bold small" data-bs-toggle="tooltip" data-bs-placement="top" title="Missed: {{ data.missed_items|join:', ' }}">
-                                                                    (-{{ data.missed }})
-                                                                </span>
-                                                            {% endif %}
-                                                        </td>
-                                                        {% endif %}
-                                                    {% endfor %}
-                                                {% endfor %}
-                                            </tr>
-                                            {% endfor %}
-                                        {% endif %}
-                                    {% endfor %}
-                                </tbody>
-                            </table>
-                        </div>
-                    </div>
+                +                <div class="card mb-4">
+                    <div class="card-header fw-bold bg-light text-secondary">
+                        <i class="bi bi-grid-3x3-gap me-2"></i>Multiplier Breakdown (Group Par)
+                    </div>
+                    <div class="card-body p-0">
+                        <table class="table table-sm table-hover mb-0 text-center align-middle">
+                            <thead class="table-dark">
+                                <tr>
+                                    <th class="text-start ps-3">Scope</th>
+                                    <th>Total Worked</th>
+                                    <th>Common</th>
+                                    {% for call in all_calls %}
+                                    <th>{{ call }}</th>
+                                    {% endfor %}
+                                </tr>
+                            </thead>
+                            <tbody>
+                                {% for row in breakdown_rows %}
+                                    {% if row.is_spacer %}
+                                        <tr class="table-light"><td colspan="{{ all_calls|length|add:3 }}">&nbsp;</td></tr>
+                                    {% else %}
+                                        <tr class="{% if row.is_bold %}fw-bold bg-light border-top border-bottom{% endif %}">
+                                            <td class="text-start ps-3">
+                                                {% if row.indent > 0 %}<span class="text-muted ms-3 small"><i class="bi bi-arrow-return-right me-1"></i></span>{% endif %}
+                                                {{ row.label }}
+                                            </td>
+                                            <td class="{% if row.is_bold %}fs-6{% endif %}">{{ row.total_worked }}</td>
+                                            <td class="text-muted">{{ row.common }}</td>
+                                            {% for call in all_calls %}
+                                                {% with stat=row.stations|get_item:call %}
+                                                <td>
+                                                    {{ stat.count }}
+                                                    {% if stat.delta < 0 %}
+                                                    <span class="text-danger small fw-bold ms-1">({{ stat.delta }})</span>
+                                                    {% endif %}
+                                                </td>
+                                                {% endwith %}
+                                            {% endfor %}
+                                        </tr>
+                                    {% endif %}
+                                {% endfor %}
+                            </tbody>
+                        </table>
+                    </div>
+                </div>
 
+                +                {% for mult in multipliers %}
+                <div class="tab-pane fade {% if forloop.first %}show active{% endif %}" id="v-pills-{{ forloop.counter }}" role="tabpanel" aria-labelledby="v-pills-{{ forloop.counter }}-tab">
                     <div class="d-flex justify-content-between align-items-center mb-3">
--- END DIFF ---