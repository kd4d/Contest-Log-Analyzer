# Sweepstakes Visualization Detailed Implementation Plan

**Date:** 2025-01-XX  
**Status:** Completed (Phases 1, 2, 4, 5) - Phase 3 Pending  
**Last Updated:** 2026-01-24  
**Category:** Planning  
**Priority:** HIGH  
**For:** New AI Agent Implementation  
**Context Window Optimized:** Yes - Self-contained with references

**Implementation Status:**
- ✅ Phase 1: Contest-Wide QSO Breakdown - Complete and verified
- ✅ Phase 2: Enhanced Missed Multipliers - Complete and verified
- ⏳ Phase 3: Multiplier Acquisition Timeline - Pending
- ✅ Phase 4: Report Suppression - Complete and verified
- ✅ Phase 5: Documentation Updates - Complete and verified

**PRIMARY REFERENCE:** `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Read this first for full context and rationale.

---

## Implementation Architecture Summary

**Code Organization:**
- **Two separate report classes**: Existing `chart_qso_breakdown.py` (unchanged initially) + new `chart_qso_breakdown_contest_wide.py`
- **Helper module**: `qso_chart_helpers.py` with module-level functions (stateless, testable)
- **Incremental refactoring**: Existing report refactored to use helpers AFTER new report is working (DRY principle)

**Report Naming Conventions:**
- Pattern: `{report_id}--{callsigns}.{ext}`
- Portable designators: `/` → `-` (single dash, not underscore)
- Callsigns joined with `_` between them
- Examples:
  - `qso_breakdown_chart_contest_wide--k3lr_w1aw.html`
  - `qso_band_distribution--k3lr_w1aw.html`
  - `enhanced_missed_multipliers--k3lr_w1aw.txt`

**Key Technical Decisions:**
1. QSO Band Distribution: New aggregator method `compute_band_distribution_breakdown()` computes symmetric difference (unique QSOs) across all bands, then shows band distribution
2. Enhanced Missed Multipliers: Extend existing `get_missed_data()` with `enhanced=True` parameter (backward compatible)
3. Multiplier Timeline: New reports following rate sheet pattern (`text_multiplier_timeline.py` and `text_multiplier_timeline_comparison.py`)
4. Run/S&P Conflicts: Use "Unknown" when logs disagree on multiplier classification (conflict between logs, not within log)
5. Dashboard Integration: Conditional tab rendering based on `dupe_check_scope == "all_bands"` detection

---

## Executive Summary

Sweepstakes contest has unique scoring rules that make standard multi-band visualizations misleading:
- **QSOs count once per contest** (`dupe_check_scope: "all_bands"`), not per band
- **Multipliers count once per contest** (`totaling_method: "once_per_log"`), not per band
- **Multiplier saturation**: Most competitors work 80+ of 85 available sections

**Problem:** Current QSO Breakdown Chart shows band-by-band breakdown, implying QSOs are counted per band. This is misleading because QSOs actually count once per contest.

**Solution:** Implement contest-wide QSO breakdown as primary view, with QSO Band Distribution as secondary view (computed differently). Also enhance missed multipliers report with Run/S&P and band context.

---

## Key Design Decisions (From Discussion Document)

**CRITICAL - Read These Before Implementing:**

1. **QSO Band Distribution**: NOT informational only - it's a DIFFERENT analysis showing band and Run/S&P distribution of stations worked by one of the two logs. "Uniques" = stations worked by one of the two stations (in one of the two logs). Categorized by band and mode like current QSO Breakdown but computed differently.

2. **Common Information**: Overall Common is very useful; Common by band is NOT useful - do NOT show Common information by band.

3. **Run/S&P Classification**: "Unknown" is CORRECT for Run/S&P conflicts (not "Mixed"). There are times when rates are so low that Run vs S&P cannot be reliably estimated. This must be emphasized in documentation.

4. **Multiplier "Available"**: ONLY defined as whether the multiplier appears in at least one of the logs being compared. We do NOT know whether a missed multiplier "could" have been worked.

5. **Multiplier Timeline**: Keep existing text report, include in bulk download, but do NOT include in dashboards.

6. **Multiplier Visualization**: Do NOT pursue multiplier visualization at this time - focus on text summary.

**Reference:** See `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` sections "Key Design Decisions" and "Open Questions Resolved" for full details.

---

## Phase 1: Contest-Wide QSO Breakdown Report

### Implementation Architecture Decision

**Approach:** Create new report class with shared helper module (incremental refactoring)

**Rationale:**
- Two separate report classes for clarity and maintainability
- Helper module with module-level functions (stateless, testable)
- Existing report remains unchanged initially (backward compatible)
- Refactor existing report to use helpers AFTER new report is working (DRY principle)

**Files to Create:**
1. `contest_tools/reports/qso_chart_helpers.py` - Module-level helper functions
2. `contest_tools/reports/chart_qso_breakdown_contest_wide.py` - New report class

**Files to Modify (Later):**
- `contest_tools/reports/chart_qso_breakdown.py` - Refactor to use helpers after Phase 1 complete

### 1.1 Create Helper Module

**File:** `contest_tools/reports/qso_chart_helpers.py` (NEW)

**Purpose:** Shared module-level functions for QSO breakdown chart generation

**Functions to Implement:**
- `build_qso_chart_filename(report_id, logs, suffix="")` - Standardized filename generation
- `apply_qso_chart_styling(fig, title_lines, footer_text)` - Common Plotly styling
- `save_qso_chart_files(fig, output_path, base_filename)` - Save HTML/JSON files
- `prepare_qso_chart_title(logs, chart_type, scope)` - Title generation
- Other common utilities as needed

**Pattern:** Follow existing `report_utils.py` pattern but for chart-specific code

### 1.2 Understand Current Implementation

**File:** `contest_tools/reports/chart_qso_breakdown.py`

**Current Behavior:**
- Shows one subplot per band
- Uses `CategoricalAggregator.compute_comparison_breakdown()` with band filter
- Displays unique/common QSOs per band
- Implies QSOs are counted per band (misleading for Sweepstakes)

**Key Code Sections:**
- `generate()` method (lines 91-283): Main generation logic
- `_prepare_data()` method (lines 46-88): Data preparation with band filter
- Uses `CategoricalAggregator.compute_comparison_breakdown()` with `band_filter=band`

**Reference:** Read `contest_tools/data_aggregators/categorical_stats.py` to understand `CategoricalAggregator.compute_comparison_breakdown()` method.

**Note:** This file will be refactored later to use helpers, but remains unchanged for Phase 1.

### 1.3 Create New Aggregator Method

**File:** `contest_tools/data_aggregators/categorical_stats.py`

**New Method:** `compute_band_distribution_breakdown(log1, log2, include_dupes=False)`

**Purpose:** For contest-wide QSO counting, compute band distribution of unique QSOs

**Logic:**
1. Get ALL QSOs (no band filter) to compute common set across all bands
2. Compute common QSOs: `common_calls = set(df1_all['Call'].unique()) & set(df2_all['Call'].unique())`
3. Compute symmetric difference (unique to each log):
   - `log1_unique_calls = set(df1_all['Call'].unique()) - common_calls`
   - `log2_unique_calls = set(df2_all['Call'].unique()) - common_calls`
4. For each band, filter unique QSOs worked on that band
5. Categorize by Run/S&P/Unknown for each log per band

**Return Structure:**
```python
{
    'bands': {
        '20M': {
            'log1': {'run': X, 'sp': Y, 'unk': Z},
            'log2': {'run': X, 'sp': Y, 'unk': Z}
        },
        ...
    }
}
```

**Key Points:**
- "Uniques" = symmetric difference (not per-band uniques)
- A station can only be worked once for credit (contest-wide)
- No "Common" category in band distribution (per design decision)

### 1.4 Create New Report Class

**File:** `contest_tools/reports/chart_qso_breakdown_contest_wide.py` (NEW)

**Report ID:** `qso_breakdown_chart_contest_wide`

**Report Name:** `QSO Breakdown - Contest Wide`

**Report Type:** `chart`

**Supports:** `supports_pairwise = True`

**Implementation Steps:**

1. **Detect Contest-Wide QSO Counting:**
   ```python
   contest_def = self.log1.contest_definition
   is_contest_wide_qso = getattr(contest_def, 'dupe_check_scope', None) == 'all_bands'
   if not is_contest_wide_qso:
       return []  # Skip if not contest-wide
   ```

2. **Generate Contest-Wide QSO Breakdown (Primary View):**
   - Call `CategoricalAggregator.compute_comparison_breakdown()` without band filter
   - Create single stacked bar chart
   - Categories: `[log1_call, "Common", log2_call]`
   - Stacked by: `['Run', 'S&P', 'Mixed/Unk']`
   - Use helper functions for styling and file saving
   - Filename: `qso_breakdown_chart_contest_wide--{callsigns}.html`

3. **Generate QSO Band Distribution (Secondary View):**
   - Call new `compute_band_distribution_breakdown()` method
   - Create subplots (one per band)
   - Each subplot: Two bars (Log1, Log2) stacked by Run/S&P/Unknown
   - Categories: `[log1_call, log2_call]` (NO "Common" category)
   - Use helper functions for styling and file saving
   - Filename: `qso_band_distribution--{callsigns}.html`

**Key Points:**
- Overall "Common" information is very useful (primary view)
- Band distribution shows symmetric difference, not per-band uniques
- Use helper module for common code
- Follow filename convention: `{report_id}--{callsigns}.{ext}`

### 1.5 Dashboard Integration

**File:** `web_app/analyzer/views.py`

**Function:** `qso_dashboard(request, session_id)`

**Implementation Steps:**

1. **Detect contest-wide QSO counting:**
   ```python
   contest_def = logs[0].contest_definition if logs else None
   is_contest_wide_qso = getattr(contest_def, 'dupe_check_scope', None) == 'all_bands'
   ```

2. **Discover reports:**
   - Look for `qso_breakdown_chart_contest_wide` report
   - Look for `qso_band_distribution` report
   - Use existing manifest discovery pattern

3. **Update context:**
   ```python
   context = {
       ...
       'is_contest_wide_qso': is_contest_wide_qso,
       'contest_wide_qso_report': contest_wide_report_path,
       'band_distribution_report': band_distribution_report_path,
       ...
   }
   ```

4. **Update template:** `web_app/analyzer/templates/analyzer/qso_dashboard.html`
   - Add conditional tabs for contest-wide view
   - Make "Contest Total" the active/default tab when contest-wide QSO counting detected
   - Keep existing band-by-band tabs for non-contest-wide contests

**Template Pattern:**
```django
{% if is_contest_wide_qso %}
<li class="nav-item">
    <button class="nav-link active" id="contest-total-tab" ...>
        Contest Total
    </button>
</li>
<li class="nav-item">
    <button class="nav-link" id="band-distribution-tab" ...>
        Band Distribution
    </button>
</li>
{% else %}
<!-- Existing band-by-band tabs -->
{% endif %}
```

### 1.6 Testing Phase 1

**Status:** ✅ Implementation Complete - Ready for Testing

**Test Cases:**
1. Load Sweepstakes logs (CW or PH) with two logs
2. Verify contest-wide QSO breakdown displays correctly
3. Verify QSO Band Distribution displays correctly
4. Verify "Common" is shown in contest-wide view but NOT in band distribution
5. Verify dashboard shows correct tabs ("Contest Total" active, "Band Distribution" available)
6. Test with non-Sweepstakes contest (should show existing band-by-band view)
7. Verify helper functions work correctly
8. Verify filename conventions are followed (`--` separator, `/` to `-` conversion)
9. Verify both HTML and JSON files are generated
10. Verify reports are discoverable in manifest

**Implementation Notes:**
- Helper module created: `qso_chart_helpers.py`
- Aggregator method added: `compute_band_distribution_breakdown()`
- Report class created: `chart_qso_breakdown_contest_wide.py`
- Dashboard view updated: Contest-wide detection and report discovery
- Template updated: Conditional tabs for contest-wide vs standard view
- Report auto-discovery: No manual registration needed (via `__init__.py`)

**Next Steps After Testing:**
- If tests pass: Proceed to Phase 2 (Enhanced Missed Multipliers)
- If issues found: Fix and retest before proceeding
- Consider refactoring existing `chart_qso_breakdown.py` to use helpers (incremental refactoring)

### 1.5 Dashboard Integration

**File:** `web_app/analyzer/views.py`

**Function:** `qso_dashboard(request, session_id)`

**Implementation Steps:**

1. **Detect contest-wide QSO counting:**
   ```python
   # Get contest definition from first log
   contest_def = logs[0].contest_definition if logs else None
   is_contest_wide_qso = getattr(contest_def, 'dupe_check_scope', None) == 'all_bands'
   ```

2. **Discover reports:**
   - Look for `qso_breakdown_chart_contest_wide` report (or similar naming)
   - Look for `qso_band_distribution` report (or similar naming)
   - Use existing manifest discovery pattern

3. **Update context:**
   ```python
   context = {
       ...
       'is_contest_wide_qso': is_contest_wide_qso,
       'contest_wide_qso_report': contest_wide_report_path,
       'band_distribution_report': band_distribution_report_path,
       ...
   }
   ```

4. **Update template:** `web_app/analyzer/templates/analyzer/qso_dashboard.html`
   - Add conditional tab for "Contest Total" when `is_contest_wide_qso == True`
   - Add conditional tab for "Band Distribution" when `is_contest_wide_qso == True`
   - Make "Contest Total" the active/default tab when contest-wide QSO counting detected

**Template Pattern:**
```django
{% if is_contest_wide_qso %}
<li class="nav-item">
    <button class="nav-link active" id="contest-total-tab" ...>
        Contest Total
    </button>
</li>
<li class="nav-item">
    <button class="nav-link" id="band-distribution-tab" ...>
        Band Distribution
    </button>
</li>
{% else %}
<!-- Existing band-by-band tabs -->
{% endif %}
```

### 1.6 Testing Phase 1

**Test Cases:**
1. Load Sweepstakes logs (CW or PH)
2. Verify contest-wide QSO breakdown displays correctly
3. Verify QSO Band Distribution displays correctly
4. Verify "Common" is shown in contest-wide view but NOT in band distribution
5. Verify dashboard shows correct tabs
6. Test with non-Sweepstakes contest (should show existing band-by-band view)

---

## Phase 2: Enhanced Missed Multipliers Report

### 2.1 Understand Current Multiplier Reports

**Files to Review:**
- `contest_tools/reports/text_multiplier_breakdown.py` - Existing text report
- `contest_tools/reports/text_missed_multipliers.py` - Existing missed multipliers report
- `contest_tools/data_aggregators/multiplier_stats.py` - Multiplier aggregator
- `web_app/analyzer/views.py` - `multiplier_dashboard()` function

**Current Behavior:**
- Text-based missed multipliers report exists (`text_missed_multipliers.py`)
- Uses `MultiplierStatsAggregator.get_missed_data()` method
- May not include Run/S&P breakdown
- May not include band distribution for missed multipliers

**Reference:** Read existing multiplier reports to understand current structure.

### 2.2 Enhance Multiplier Aggregator

**File:** `contest_tools/data_aggregators/multiplier_stats.py`

**Action:** Extend existing `get_missed_data()` method with `enhanced=True` parameter

**Approach:** Extend existing method (backward compatible) rather than creating new method

**Method Signature:**
```python
def get_missed_data(self, mult_name: str, mode_filter: str = None, enhanced: bool = False) -> Dict[str, Any]:
    """
    Computes enhanced missed multipliers breakdown with Run/S&P and band context.
    
    Returns:
        {
            'missed_multipliers': [
                {
                    'section': 'WMA',
                    'worked_by': ['log1'],  # Which log(s) worked it
                    'worked_by_count': 1,   # Count of logs that worked it
                    'bands': ['20M', '40M'],  # Bands where worked (if worked)
                    'run_count': 1,  # Run QSOs (if worked)
                    'sp_count': 1,   # S&P QSOs (if worked)
                    'unk_count': 0   # Unknown QSOs (if worked)
                },
                ...
            ]
        }
    """
```

**Implementation Logic (when enhanced=True):**

1. **Use existing `get_missed_data()` logic** to identify missed multipliers
2. **For each missed multiplier, if worked by any log:**
   - Extract band distribution (which bands it was worked on)
   - Extract Run/S&P/Unknown counts per multiplier
   - Note: Multipliers count once per contest in same log
   - First occurrence determines mode and band
   - For conflicts between logs (different classifications), use "Unknown"

3. **Enhanced Return Structure:**
   ```python
   {
       # Existing structure from get_missed_data()...
       'enhanced_breakdown': [
           {
               'section': 'WMA',
               'worked_by': ['log1'],  # Which log(s) worked it
               'worked_by_count': 1,   # Count of logs that worked it
               'bands': ['20M', '40M'],  # Bands where worked (if worked)
               'run_count': 1,  # Run QSOs (if worked)
               'sp_count': 1,   # S&P QSOs (if worked)
               'unk_count': 0   # Unknown QSOs (if worked)
           },
           ...
       ]
   }
   ```

**Important:**
- Use "Unknown" for Run/S&P conflicts between logs (not "Mixed")
- "Available" is ONLY defined as appearing in at least one log
- Do NOT imply knowledge about whether multiplier "could" have been worked
- Run/S&P classification comes from log parsing (per QSO)
- Multipliers count once per contest in same log (first occurrence determines mode/band)

### 2.3 Create Enhanced Missed Multipliers Text Report

**File:** `contest_tools/reports/text_enhanced_missed_multipliers.py` (NEW)

**Report ID:** `enhanced_missed_multipliers`

**Report Name:** `Enhanced Missed Multipliers Breakdown`

**Report Type:** `text`

**Supports:** `supports_pairwise = True`, `supports_multi = True`

**Format:** Text table with structured columns

**Table Structure:**
```
Section | Worked By | Bands Worked | Run | S&P | Unknown
--------|-----------|--------------|-----|-----|--------
WMA     | 1 of 2    | 20M, 40M     | 1   | 1   | 0
CT      | 0 of 2    | --           | --  | --  | --
...
```

**Implementation Steps:**

1. **Get enhanced breakdown from aggregator:**
   ```python
   mult_agg = MultiplierStatsAggregator(logs)
   breakdown = mult_agg.get_missed_data(mult_name, mode_filter, enhanced=True)
   # Access enhanced_breakdown from return structure
   ```

2. **Format table:**
   ```python
   lines = []
   lines.append("Enhanced Missed Multipliers Breakdown")
   lines.append("=" * 80)
   lines.append("")
   lines.append(f"{'Section':<12} {'Worked By':<12} {'Bands Worked':<20} {'Run':<6} {'S&P':<6} {'Unknown':<8}")
   lines.append("-" * 80)
   
   enhanced_data = breakdown.get('enhanced_breakdown', [])
   for item in enhanced_data:
       section = item['section']
       worked_by = f"{item['worked_by_count']} of {len(logs)}"
       bands = ', '.join(item.get('bands', [])) if item.get('bands') else '--'
       run = str(item.get('run_count', '--'))
       sp = str(item.get('sp_count', '--'))
       unk = str(item.get('unk_count', '--'))
       
       lines.append(f"{section:<12} {worked_by:<12} {bands:<20} {run:<6} {sp:<6} {unk:<8}")
   ```

3. **Save to file:**
   ```python
   from contest_tools.utils.callsign_utils import build_callsigns_filename_part
   all_calls = sorted([log.get_metadata().get('MyCall', 'Unknown') for log in logs])
   callsigns_part = build_callsigns_filename_part(all_calls)
   filename = f"enhanced_missed_multipliers--{callsigns_part}.txt"
   output_file = os.path.join(output_path, filename)
   with open(output_file, 'w') as f:
       f.write('\n'.join(lines))
   ```

**Key Points:**
- Use existing `get_missed_data()` with `enhanced=True` parameter
- Follow filename convention: `{report_id}--{callsigns}.txt`
- Include standard header/footer using `get_standard_title_lines()` and `get_standard_footer()`

### 2.4 Dashboard Integration

**File:** `web_app/analyzer/views.py`

**Function:** `multiplier_dashboard(request, session_id)`

**Implementation:**
- Discover enhanced missed multipliers report from manifest
- Add to appropriate tab in Multiplier Dashboard
- Display as text content or link to file

**Template:** `web_app/analyzer/templates/analyzer/multiplier_dashboard.html`
- Add section for enhanced missed multipliers report
- Display text content in `<pre>` tag or link to file

### 2.5 Testing Phase 2

**Test Cases:**
1. Load Sweepstakes logs with missed multipliers
2. Verify enhanced missed multipliers report shows correct data
3. Verify Run/S&P breakdown is accurate
4. Verify band distribution is shown for worked multipliers
5. Verify "Unknown" is used for Run/S&P conflicts
6. Verify dashboard displays report correctly

---

## Phase 3: Multiplier Acquisition Timeline (Text Report)

### 3.1 Understand Requirements

**Current State:**
- `text_breakdown_report.py` contains multiplier data as part of WriteLog breakdown (QSO/Mult by hour)
- This report should be retained as-is
- Need separate multiplier acquisition timeline report showing when each multiplier is FIRST worked

**Requirements:**
- Show hourly progression of unique multipliers (when each multiplier is first worked)
- Support single-log and multi-log comparison (like rate sheet reports)
- Follow rate sheet report structure pattern
- Use `TimeSeriesAggregator` data (`new_mults_by_band` or `new_mults_by_mode`)

### 3.2 Create Multiplier Timeline Reports

**Files to Create:**
1. `contest_tools/reports/text_multiplier_timeline.py` - Single-log version
2. `contest_tools/reports/text_multiplier_timeline_comparison.py` - Multi-log comparison version

**Report IDs:**
- `multiplier_timeline` (single)
- `multiplier_timeline_comparison` (multi-log)

**Pattern:** Follow `text_rate_sheet.py` and `text_rate_sheet_comparison.py` structure

**Implementation:**
- Use `TimeSeriesAggregator.get_time_series_data()`
- Track first occurrence of each multiplier per hour
- Display format: Hour | Call | [Multiplier columns...] | Total | Cumul
- Filename: `multiplier_timeline--{callsign}.txt` or `multiplier_timeline_comparison--{callsigns}.txt`

### 3.3 Include in Bulk Download

**File:** `web_app/analyzer/views.py`

**Function:** `download_all_reports(request, session_id)` or similar

**Implementation:**
- Multiplier timeline reports will be automatically included in bulk download
- Use existing bulk download pattern (discovers all reports from manifest)
- No special handling needed

### 3.4 Exclude from Dashboards

**File:** `web_app/analyzer/views.py`

**Function:** `multiplier_dashboard(request, session_id)`

**Implementation:**
- When discovering reports, exclude multiplier timeline reports
- Use report ID pattern to filter
- Keep in bulk download but exclude from dashboard display

**Pattern:**
```python
# Discover reports
all_reports = discover_reports_from_manifest(...)

# Filter out timeline reports from dashboard
dashboard_reports = [
    r for r in all_reports 
    if 'multiplier_timeline' not in r['report_id']
]
```

### 3.4 Testing Phase 3

**Test Cases:**
1. Verify multiplier acquisition timeline report exists
2. Verify it's included in bulk download
3. Verify it's NOT displayed in dashboards
4. Test with Sweepstakes logs

---

## Phase 4: Report Suppression and Configuration

### 4.1 Understand Report Suppression

**Current State:** Check if `excluded_reports` configuration exists in contest definitions

**File:** `contest_tools/contest_definitions/arrl_ss.json`

**Check:** Does it have `excluded_reports` field? If so, what's in it?

**Reference:** Check other contest definitions (e.g., `cq_wpx_ssb.json`) for `excluded_reports` pattern.

### 4.2 Configure Report Suppression for Sweepstakes

**File:** `contest_tools/contest_definitions/arrl_ss.json`

**Action:** Add or update `excluded_reports` field

**Decision Needed:** Which reports should be suppressed?
- Standard band-by-band QSO breakdown? (Yes - replaced by contest-wide)
- Other reports? (Check with user or review discussion)

**Example:**
```json
{
  "excluded_reports": [
    "qso_breakdown_chart"  // Suppress standard band-by-band version
  ]
}
```

**Note:** May need to keep standard report for non-Sweepstakes contests, so suppression should be contest-specific.

### 4.3 Implement Report Suppression Logic

**File:** `contest_tools/report_generator.py`

**Action:** Check `excluded_reports` before generating reports

**Implementation Pattern:**
```python
def generate_reports(self, logs, output_path):
    contest_def = logs[0].contest_definition
    excluded = getattr(contest_def, 'excluded_reports', [])
    
    for report_class in available_reports:
        if report_class.report_id in excluded:
            continue  # Skip this report
        
        # Generate report
        report = report_class(logs)
        report.generate(output_path)
```

**Reference:** Check existing report generator implementation for current pattern.

### 4.4 Testing Phase 4

**Test Cases:**
1. Verify excluded reports are not generated for Sweepstakes
2. Verify non-excluded reports are still generated
3. Verify other contests are not affected
4. Test report generation with Sweepstakes logs

---

## Phase 5: Documentation Updates

### 5.1 Web Documentation

**Files:**
- `Docs/ReportInterpretationGuide.md` - User-facing documentation
- Web help pages (if separate)

**Content to Add:**

1. **Sweepstakes-Specific Visualizations Section:**
   - Contest-wide QSO counting explanation
   - Why contest-wide QSO breakdown is needed
   - QSO Band Distribution explanation (different from standard breakdown)
   - Enhanced missed multipliers explanation

2. **Run/S&P "Unknown" Classification:**
   - Explain that "Unknown" is a valid classification
   - Emphasize that rates may be too low to reliably estimate Run vs S&P
   - This is NOT a data quality issue
   - Particularly important for Sweepstakes

**Location:** Add new section or enhance existing section

### 5.2 Off-Line Documentation

**File:** `Docs/UsersGuide.md` or similar

**Action:** Add same content as web documentation

**Format:** Markdown, consistent with existing documentation style

### 5.3 Code Documentation

**Files:**
- `contest_tools/reports/chart_qso_breakdown.py`
- `contest_tools/data_aggregators/multiplier_stats.py`
- `contest_tools/data_aggregators/categorical_stats.py` (if enhanced)

**Action:** Add comments explaining Sweepstakes-specific logic

**Comments to Add:**

1. **In chart_qso_breakdown.py:**
   ```python
   # Sweepstakes-specific: Contest-wide QSO counting
   # QSOs count once per contest (dupe_check_scope: "all_bands")
   # Standard band-by-band breakdown is misleading
   # Use contest-wide breakdown as primary view
   ```

2. **In multiplier_stats.py:**
   ```python
   # Run/S&P Classification: "Unknown" is correct for conflicts
   # There are times when rates are so low that Run vs S&P
   # cannot be reliably estimated. "Unknown" is a valid classification,
   # not a data quality issue.
   ```

3. **In categorical_stats.py (if enhanced):**
   ```python
   # QSO Band Distribution: Different computation for Sweepstakes
   # "Uniques" = stations worked by one of the two logs
   # Do NOT show "Common" by band (not useful)
   # Overall Common is useful, but Common by band is not
   ```

### 5.4 Testing Phase 5

**Test Cases:**
1. Verify documentation is clear and helpful
2. Verify "Unknown" classification is explained
3. Verify Sweepstakes-specific features are documented
4. Review documentation for accuracy

---

## Implementation Checklist

### Phase 1: Contest-Wide QSO Breakdown ✅ COMPLETE
- [x] Read and understand current `chart_qso_breakdown.py` implementation
- [x] Create helper module `qso_chart_helpers.py` with module-level functions
- [x] Add `compute_band_distribution_breakdown()` method to `CategoricalAggregator`
- [x] Create new report class `chart_qso_breakdown_contest_wide.py`
- [x] Implement contest-wide QSO breakdown chart (primary view)
- [x] Implement QSO Band Distribution chart (secondary view, computed differently)
- [x] Update `qso_dashboard()` view with contest-wide detection logic
- [x] Update `qso_dashboard.html` template with conditional tabs
- [x] Register new report (auto-discovered via `__init__.py`)
- [x] **Verified: Tested with Sweepstakes logs - working correctly**
- [x] **Verified: Tested with non-Sweepstakes contest - existing view preserved**
- [x] **Verified: Both charts generate correctly**
- [x] **Verified: Dashboard shows correct tabs**

### Phase 2: Enhanced Missed Multipliers ✅ COMPLETE
- [x] Read existing multiplier reports
- [x] Enhance `MultiplierStatsAggregator` with `enhanced=True` parameter
- [x] Create enhanced missed multipliers text report (`text_enhanced_missed_multipliers.py`)
- [x] Ensure "Unknown" is used for Run/S&P conflicts
- [x] Update dashboard to display enhanced report
- [x] Test with Sweepstakes logs - verified working

### Phase 3: Multiplier Timeline
- [ ] Locate existing multiplier acquisition timeline report
- [ ] Verify it works for Sweepstakes
- [ ] Include in bulk download
- [ ] Exclude from dashboards
- [ ] Test bulk download and dashboard

### Phase 4: Report Suppression ✅ COMPLETE
- [x] Check current `excluded_reports` implementation
- [x] Configure Sweepstakes to suppress inappropriate reports (`arrl_ss.json`)
- [x] Implement suppression logic - verified working in `report_generator.py`
- [x] Test report generation - verified `qso_breakdown_chart` suppressed correctly

### Phase 5: Documentation ✅ COMPLETE
- [x] Update web documentation (ReportInterpretationGuide, UsersGuide, ProgrammersGuide)
- [x] Update off-line documentation (web help templates)
- [x] Add code comments (Sweepstakes-specific logic documented)
- [x] Review for accuracy - verified complete

---

## Key Files Modified/Created

### Phase 1: ✅ COMPLETE

#### Files Created
- `contest_tools/reports/qso_chart_helpers.py` - Helper module with module-level functions
- `contest_tools/reports/chart_qso_breakdown_contest_wide.py` - New report class for contest-wide QSO breakdown

#### Files Modified
- `contest_tools/data_aggregators/categorical_stats.py` - Added `compute_band_distribution_breakdown()` method
- `web_app/analyzer/views.py` - Updated `qso_dashboard()` with contest-wide detection and report discovery
- `web_app/analyzer/templates/analyzer/qso_dashboard.html` - Added conditional tabs for contest-wide view

#### Files Unchanged (For Now)
- `contest_tools/reports/chart_qso_breakdown.py` - Existing report unchanged (will refactor later to use helpers)

### Phase 2: Enhanced Missed Multipliers (Pending)

#### Files to Modify
- `contest_tools/data_aggregators/multiplier_stats.py` - Extend `get_missed_data()` with `enhanced=True` parameter
- `contest_tools/reports/text_enhanced_missed_multipliers.py` - New report class (to be created)
- `web_app/analyzer/views.py` - Update `multiplier_dashboard()` to display enhanced report
- `web_app/analyzer/templates/analyzer/multiplier_dashboard.html` - Add enhanced report display

### Phase 3: Multiplier Timeline (Pending)

#### Files to Create
- `contest_tools/reports/text_multiplier_timeline.py` - Single-log multiplier timeline
- `contest_tools/reports/text_multiplier_timeline_comparison.py` - Multi-log comparison timeline

#### Files to Modify
- `web_app/analyzer/views.py` - Update `download_all_reports()` and `multiplier_dashboard()` to include/exclude timeline

### Phase 4: Report Suppression (Pending)

#### Files to Modify
- `contest_tools/contest_definitions/arrl_ss.json` - Add `excluded_reports` configuration if needed
- `contest_tools/report_generator.py` - Verify suppression logic works (already implemented)

### Phase 5: Documentation (Pending)

#### Files to Modify
- `Docs/ReportInterpretationGuide.md` - User-facing documentation
- `Docs/UsersGuide.md` - User guide
- Code files - Add comments explaining Sweepstakes-specific logic

---

## Testing Strategy

### Unit Tests
- Test aggregator methods with sample data
- Test report generation with mock logs
- Test detection logic for contest-wide QSO counting

### Integration Tests
- Test full report generation with Sweepstakes logs
- Test dashboard discovery and display
- Test report suppression

### Manual Testing
- Load Sweepstakes CW logs
- Load Sweepstakes PH logs (separate contest)
- Verify all reports generate correctly
- Verify dashboard displays correctly
- Verify bulk download includes all reports
- Test with non-Sweepstakes contest (should not break)

---

## Success Criteria

### Functional
- [ ] Contest-wide QSO breakdown displays correctly for Sweepstakes
- [ ] QSO Band Distribution shows correct data (no Common by band)
- [ ] Enhanced missed multipliers report shows all required information
- [ ] Multiplier timeline included in bulk download
- [ ] Multiplier timeline excluded from dashboards
- [ ] Inappropriate reports suppressed for Sweepstakes
- [ ] Non-Sweepstakes contests still work correctly

### Quality
- [ ] Run/S&P "Unknown" classification used correctly
- [ ] Documentation explains "Unknown" classification
- [ ] Code comments explain Sweepstakes-specific logic
- [ ] All reports generate without errors
- [ ] Dashboard integration works correctly

### User Experience
- [ ] Contest-wide QSO breakdown is primary view for Sweepstakes
- [ ] QSO Band Distribution is accessible as secondary view
- [ ] Enhanced missed multipliers report is easy to find and read
- [ ] Documentation helps users understand Sweepstakes-specific features

---

## Implementation Decisions Made

1. **QSO Band Distribution Aggregator**: New method `compute_band_distribution_breakdown()` in `CategoricalAggregator` - computes symmetric difference (unique QSOs) and shows band distribution
2. **Report Naming**: 
   - Contest-wide: `qso_breakdown_chart_contest_wide`
   - Band distribution: `qso_band_distribution`
   - Enhanced missed multipliers: `enhanced_missed_multipliers`
   - Multiplier timeline: `multiplier_timeline` and `multiplier_timeline_comparison`
   - Filename pattern: `{report_id}--{callsigns}.{ext}` (portable designators: `/` → `-`)
3. **Dashboard Tab Labels**: "Contest Total" (primary), "Band Distribution" (secondary)
4. **Multiplier Report**: Extend existing `get_missed_data()` with `enhanced=True` parameter (backward compatible)
5. **Multiplier Timeline**: New reports following rate sheet pattern
6. **Code Organization**: 
   - Two separate report classes (existing + new)
   - Helper module: `qso_chart_helpers.py` with module-level functions
   - Incremental refactoring: existing report refactored AFTER new one works
7. **Run/S&P Conflicts**: Use "Unknown" when logs disagree on multiplier classification

---

## References

**PRIMARY:** `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Read this first for full context, rationale, and design decisions.

**Secondary:**
- `contest_tools/contest_definitions/arrl_ss.json` - Sweepstakes contest definition
- `DevNotes/FUTURE_WORK.md` - Committed work items
- `Docs/AI_AGENT_RULES.md` - Project rules and patterns
- `Docs/ProgrammersGuide.md` - Architecture and patterns

**Code References:**
- `contest_tools/reports/chart_qso_breakdown.py` - Current QSO breakdown implementation
- `contest_tools/data_aggregators/categorical_stats.py` - Categorical aggregator
- `contest_tools/data_aggregators/multiplier_stats.py` - Multiplier aggregator
- `web_app/analyzer/views.py` - Dashboard views

---

## Notes for AI Agent

1. **Read Discussion Document First:** `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` contains all context and rationale. Read it completely before starting.

2. **Key Misconceptions to Avoid:**
   - QSO Band Distribution is NOT just "informational" - it's a different analysis
   - "Common" by band is NOT useful - only overall Common is useful
   - "Unknown" is CORRECT for Run/S&P conflicts (not "Mixed")
   - "Available" is ONLY defined as appearing in at least one log

3. **Follow Existing Patterns:**
   - Use existing report generation patterns
   - Use existing aggregator patterns
   - Use existing dashboard discovery patterns
   - Follow DAL (Data Aggregation Layer) pattern - reports format data, aggregators process data

4. **Test Incrementally:**
   - Test each phase before moving to next
   - Test with Sweepstakes logs
   - Test with non-Sweepstakes logs to ensure no regression

5. **Documentation is Critical:**
   - Must explain "Unknown" classification
   - Must explain Sweepstakes-specific features
   - Must emphasize that "Unknown" is valid, not a data quality issue

## Phase 1 Implementation Summary ✅

**Status:** Implementation Complete and Verified - Fully operational

### Files Created
- ✅ `contest_tools/reports/qso_chart_helpers.py` - Helper module with module-level functions
  - `build_qso_chart_filename()` - Standardized filename generation
  - `apply_qso_chart_styling()` - Common Plotly styling
  - `save_qso_chart_files()` - Save HTML/JSON files
  - `prepare_qso_chart_title()` - Title generation

- ✅ `contest_tools/reports/chart_qso_breakdown_contest_wide.py` - New report class
  - Report ID: `qso_breakdown_chart_contest_wide`
  - Generates two charts: Contest-Wide QSO Breakdown (primary) and QSO Band Distribution (secondary)
  - Auto-discovered via `reports/__init__.py`

### Files Modified
- ✅ `contest_tools/data_aggregators/categorical_stats.py`
  - Added `compute_band_distribution_breakdown()` method
  - Computes symmetric difference (unique QSOs) and shows band distribution

- ✅ `web_app/analyzer/views.py`
  - Updated `qso_dashboard()` function
  - Added contest-wide detection: `dupe_check_scope == "all_bands"`
  - Added report discovery for contest-wide and band distribution reports

- ✅ `web_app/analyzer/templates/analyzer/qso_dashboard.html`
  - Added conditional tabs for contest-wide view
  - "Contest Total" tab (active when contest-wide detected)
  - "Band Distribution" tab (secondary when contest-wide detected)
  - Existing tabs shown when NOT contest-wide

### Key Implementation Decisions
- ✅ Two separate report classes (existing + new) for clarity and maintainability
- ✅ Helper module with module-level functions (stateless, testable)
- ✅ Incremental refactoring approach (existing report unchanged initially)
- ✅ Filename convention: `{report_id}--{callsigns}.{ext}` (portable designators: `/` → `-`)

### Testing Verified ✅
1. ✅ **Loaded Sweepstakes logs (CW and PH)** with multiple logs
2. ✅ **Verified contest-wide QSO breakdown** displays correctly
   - Shows Log1 Unique | Common | Log2 Unique
   - Stacked by Run, S&P, Mixed/Unk
3. ✅ **Verified QSO Band Distribution** displays correctly
   - Shows unique QSOs per band (symmetric difference)
   - NO "Common" category in band distribution
   - Two bars per band (Log1, Log2)
4. ✅ **Verified dashboard tabs** work correctly
   - "Contest Total" tab is active by default
   - "Band Distribution" tab is accessible
5. ✅ **Tested with non-Sweepstakes contest**
   - Existing band-by-band view preserved
   - No new tabs appear for non-Sweepstakes
   - No breaking changes
6. ✅ **Verified filename conventions**
   - `qso_breakdown_chart_contest_wide--{callsigns}.html`
   - `qso_band_distribution--{callsigns}.html`
   - Portable designators: `/` → `-` (single dash)

### Implementation Status
- ✅ **Phase 1 Complete:** All functionality verified and working
- ✅ **Phase 2 Complete:** Enhanced Missed Multipliers implemented and verified
- ✅ **Phase 4 Complete:** Report suppression configured and working
- ✅ **Phase 5 Complete:** Documentation fully updated
- ⏳ **Phase 3 Pending:** Multiplier timeline reports not yet implemented
