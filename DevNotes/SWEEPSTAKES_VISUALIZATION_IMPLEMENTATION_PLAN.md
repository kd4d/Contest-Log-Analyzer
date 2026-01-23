# Sweepstakes Visualization Implementation Plan

**Date:** 2025-01-XX  
**Status:** Phase 1 Complete - Testing Pending  
**Priority:** HIGH  
**Related:** `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md`  
**Last Updated:** Phase 1 Implementation Complete

---

## Overview

Implement contest-wide QSO breakdown and enhanced multiplier analysis for Sweepstakes contest. Sweepstakes has unique scoring rules (QSOs and multipliers count once per contest, not per band) that make standard multi-band visualizations misleading.

---

## Phase 1: Contest-Wide QSO Breakdown Report ✅ COMPLETE

### Goal
Fix misleading band-by-band QSO breakdown by implementing contest-wide QSO breakdown as primary view.

### Status
**Implementation Complete** - Ready for Testing

### Tasks Completed

#### 1.1 ✅ Created Helper Module
- **File**: `contest_tools/reports/qso_chart_helpers.py` (NEW)
- **Action**: Created module-level helper functions for chart generation
- **Functions**: `build_qso_chart_filename()`, `apply_qso_chart_styling()`, `save_qso_chart_files()`, `prepare_qso_chart_title()`

#### 1.2 ✅ Enhanced Aggregator
- **File**: `contest_tools/data_aggregators/categorical_stats.py`
- **Action**: Added `compute_band_distribution_breakdown()` method
- **Logic**: Computes symmetric difference (unique QSOs) and shows band distribution
- **Returns**: Band distribution data structure with Run/S&P/Unknown breakdown

#### 1.3 ✅ Created New Report Class
- **File**: `contest_tools/reports/chart_qso_breakdown_contest_wide.py` (NEW)
- **Action**: Created new report class for contest-wide QSO breakdown
- **Features**:
  - Detects contest-wide QSO counting (`dupe_check_scope == "all_bands"`)
  - Generates contest-wide QSO breakdown chart (primary view)
  - Generates QSO Band Distribution chart (secondary view)
  - Uses helper functions for common operations

#### 1.4 ✅ Dashboard Integration
- **File**: `web_app/analyzer/views.py` (qso_dashboard function)
- **Action**: Added contest-wide detection and report discovery
- **File**: `web_app/analyzer/templates/analyzer/qso_dashboard.html`
- **Action**: Added conditional tabs for contest-wide view
- **Logic**: 
  - If contest-wide QSO counting detected: Show "Contest Total" (active) and "Band Distribution" tabs
  - Otherwise: Show existing band-by-band breakdown tabs

### Deliverables ✅
- ✅ Helper module: `qso_chart_helpers.py`
- ✅ Aggregator method: `compute_band_distribution_breakdown()`
- ✅ Contest-wide QSO breakdown report (HTML/JSON)
- ✅ QSO Band Distribution report (HTML/JSON)
- ✅ Dashboard integration with conditional tab structure
- ✅ Updated QSO Dashboard view and template

### Dependencies ✅
- ✅ `CategoricalAggregator` enhanced with new method
- ✅ Contest definition has `dupe_check_scope: "all_bands"` set (verified in `arrl_ss.json`)

### Next Steps (Testing Required)
1. **Test with Sweepstakes logs (CW or PH)** - Load two logs and verify:
   - Both charts generate correctly
   - Contest-wide breakdown shows Log1 Unique | Common | Log2 Unique
   - Band distribution shows unique QSOs per band (no Common category)
   - Dashboard shows "Contest Total" and "Band Distribution" tabs
   - "Contest Total" tab is active by default

2. **Test with non-Sweepstakes contest** - Verify:
   - Existing band-by-band view still works
   - No new tabs appear
   - No breaking changes

3. **Verify filename conventions**:
   - `qso_breakdown_chart_contest_wide--{callsigns}.html`
   - `qso_band_distribution--{callsigns}.html`
   - Portable designators: `/` → `-` (single dash)

4. **If tests pass**: Proceed to Phase 2 (Enhanced Missed Multipliers)
5. **If issues found**: Fix and retest before proceeding

---

## Phase 2: Enhanced Missed Multipliers Report

### Goal
Provide actionable missed multiplier analysis with Run/S&P and band context.

### Tasks

#### 2.1 Enhanced Missed Multipliers Text Report
- **File**: `contest_tools/reports/text_multiplier_breakdown.py` (or new report)
- **Action**: Create enhanced missed multipliers text report
- **Format**: Text table with structured columns
  - Section name
  - Worked by (which log(s) worked it, count)
  - Bands where it was worked (if worked by one of the logs)
  - Run vs S&P breakdown (if worked by one of the logs)
- **Data Source**: Use `MultiplierStatsAggregator` with enhanced breakdown
- **Output**: Text file (.txt)

#### 2.2 Multiplier Aggregator Enhancement
- **File**: `contest_tools/data_aggregators/multiplier_stats.py`
- **Action**: Add method to compute enhanced missed multipliers breakdown
- **Logic**:
  - Identify multipliers not worked by each log
  - For each missed multiplier, check if it was worked by other log(s) in comparison
  - Extract band distribution for worked multipliers
  - Extract Run/S&P breakdown for worked multipliers
- **Output**: Structured data for text report

#### 2.3 Run/S&P Classification
- **File**: `contest_tools/data_aggregators/multiplier_stats.py`
- **Action**: Ensure "Unknown" is used for Run/S&P conflicts
- **Logic**: 
  - When multiplier appears in both Run and S&P QSOs, classify as "Unknown"
  - "Unknown" correctly represents cases where Run/S&P cannot be reliably estimated
  - Particularly important when rates are very low
- **Documentation**: Emphasize in code comments that "Unknown" is valid classification

#### 2.4 Dashboard Integration
- **File**: `web_app/analyzer/views.py` (multiplier_dashboard function)
- **Action**: Display enhanced missed multipliers report in Multiplier Dashboard
- **Location**: Add to appropriate tab in Multiplier Dashboard
- **Format**: Display text report content or link to report file

### Deliverables
- Enhanced missed multipliers text report (text table format)
- Enhanced multiplier aggregator method
- Dashboard integration
- Documentation updates

### Dependencies
- `MultiplierStatsAggregator` must support enhanced breakdown
- Run/S&P classification logic must use "Unknown" correctly

---

## Phase 3: Multiplier Acquisition Timeline (Text Report)

### Goal
Ensure multiplier acquisition timeline text report is available for Sweepstakes.

### Tasks

#### 3.1 Verify Existing Report
- **File**: Check for existing multiplier acquisition timeline report
- **Action**: Verify report exists and works for Sweepstakes
- **Location**: Likely in `contest_tools/reports/` directory

#### 3.2 Include in Bulk Download
- **File**: `web_app/analyzer/views.py` (download_all_reports function)
- **Action**: Ensure multiplier acquisition timeline report is included in bulk download
- **Logic**: Add report to download list for Sweepstakes

#### 3.3 Exclude from Dashboards
- **File**: `web_app/analyzer/views.py` (multiplier_dashboard function)
- **Action**: Ensure multiplier acquisition timeline is NOT displayed in dashboards
- **Logic**: Exclude from dashboard display (but keep in bulk download)

### Deliverables
- Verified multiplier acquisition timeline report
- Included in bulk download
- Excluded from dashboards

### Dependencies
- Existing multiplier acquisition timeline report must exist
- Report must work correctly for Sweepstakes

---

## Phase 4: Report Suppression and Configuration

### Goal
Enable contest-specific report generation and suppression.

### Tasks

#### 4.1 Report Suppression Configuration
- **File**: `contest_tools/contest_definitions/arrl_ss.json`
- **Action**: Add `excluded_reports` configuration if needed
- **Logic**: Suppress reports that don't apply to Sweepstakes
- **Example**: May need to suppress standard band-by-band QSO breakdown

#### 4.2 Report Generation Logic
- **File**: `contest_tools/report_generator.py`
- **Action**: Implement report suppression logic
- **Logic**: Check `excluded_reports` in contest definition before generating reports
- **Output**: Skip excluded reports during generation

#### 4.3 Testing
- **Action**: Test report generation with Sweepstakes logs
- **Verify**: 
  - Contest-wide QSO breakdown is generated
  - QSO Band Distribution is generated
  - Enhanced missed multipliers is generated
  - Inappropriate reports are suppressed

### Deliverables
- Report suppression configuration
- Report generation logic updates
- Test results

### Dependencies
- Contest definition must support `excluded_reports` configuration
- Report generator must respect suppression settings

---

## Phase 5: Documentation Updates

### Goal
Update documentation to explain Sweepstakes-specific visualizations and Run/S&P "Unknown" classification.

### Tasks

#### 5.1 Web Documentation
- **File**: `Docs/ReportInterpretationGuide.md` or web help pages
- **Action**: Add section explaining Sweepstakes-specific visualizations
- **Content**:
  - Contest-wide QSO counting explanation
  - QSO Band Distribution explanation
  - Enhanced missed multipliers explanation
  - Run/S&P "Unknown" classification explanation (rates too low to estimate)

#### 5.2 Off-Line Documentation
- **File**: `Docs/UsersGuide.md` or similar
- **Action**: Add section on Sweepstakes-specific features
- **Content**: Same as web documentation

#### 5.3 Code Documentation
- **Files**: Report and aggregator files
- **Action**: Add comments explaining Sweepstakes-specific logic
- **Content**: 
  - Why "Unknown" is used for Run/S&P conflicts
  - Why contest-wide QSO breakdown is needed
  - How QSO Band Distribution differs from standard breakdown

### Deliverables
- Updated web documentation
- Updated off-line documentation
- Enhanced code comments

### Dependencies
- Implementation must be complete before documentation updates

---

## Implementation Order

### Recommended Sequence

1. **Phase 1**: Contest-Wide QSO Breakdown Report
   - Foundation for correct visualization
   - Most critical fix for misleading current display

2. **Phase 2**: Enhanced Missed Multipliers Report
   - Provides actionable insights
   - Builds on multiplier aggregator

3. **Phase 3**: Multiplier Acquisition Timeline
   - Simple verification and configuration
   - Low risk, quick to complete

4. **Phase 4**: Report Suppression and Configuration
   - Ensures only appropriate reports are generated
   - Prevents confusion from inappropriate reports

5. **Phase 5**: Documentation Updates
   - Documents new features and concepts
   - Helps users understand Sweepstakes-specific behavior

### Why This Order?

- **Phase 1 First**: Fixes the most misleading visualization (band-by-band QSO breakdown)
- **Phase 2 Second**: Provides valuable multiplier insights
- **Phase 3 Third**: Simple verification task, low risk
- **Phase 4 Fourth**: Configuration to ensure clean report generation
- **Phase 5 Last**: Documentation after implementation is complete

---

## Success Criteria

### Functional Requirements
- [ ] Contest-wide QSO breakdown displays correctly for Sweepstakes
- [ ] QSO Band Distribution shows band and Run/S&P distribution correctly
- [ ] Enhanced missed multipliers report shows all required information
- [ ] Multiplier acquisition timeline included in bulk download
- [ ] Multiplier acquisition timeline excluded from dashboards
- [ ] Inappropriate reports are suppressed for Sweepstakes

### Quality Requirements
- [ ] Run/S&P "Unknown" classification used correctly
- [ ] Documentation explains "Unknown" classification (rates too low)
- [ ] Code comments explain Sweepstakes-specific logic
- [ ] All reports generate without errors
- [ ] Dashboard integration works correctly

### User Experience Requirements
- [ ] Contest-wide QSO breakdown is primary view for Sweepstakes
- [ ] QSO Band Distribution is accessible as secondary view
- [ ] Enhanced missed multipliers report is easy to find and read
- [ ] Documentation helps users understand Sweepstakes-specific features

---

## Technical Notes

### Key Implementation Details

1. **Contest Detection**: Use `dupe_check_scope: "all_bands"` to detect contest-wide QSO counting
2. **QSO Band Distribution**: Compute "uniques" differently - stations worked by one of the two logs
3. **Run/S&P Classification**: Use "Unknown" for conflicts, not "Mixed"
4. **Multiplier "Available"**: Only defined as appearing in at least one log being compared
5. **Common Information**: Overall Common is useful; Common by band is NOT useful

### Dependencies

- `CategoricalAggregator` may need enhancement
- `MultiplierStatsAggregator` may need enhancement
- Contest definition must have correct configuration
- Report generator must support suppression

### Testing Strategy

1. Test with Sweepstakes logs (CW and PH separately)
2. Verify contest-wide QSO breakdown displays correctly
3. Verify QSO Band Distribution shows correct data
4. Verify enhanced missed multipliers report is accurate
5. Verify inappropriate reports are suppressed
6. Verify documentation is clear and helpful

---

## Questions & Decisions Needed

### Open Questions

1. **QSO Band Distribution Aggregator**: Does `CategoricalAggregator` need new method, or can existing method be used with different parameters?
2. **Report Naming**: What should the new reports be named? (e.g., `chart_qso_breakdown_contest_wide.html`)
3. **Dashboard Tab Labels**: What should the tabs be labeled? (e.g., "Contest Total", "Band Distribution")
4. **Multiplier Report Location**: Should enhanced missed multipliers be a new report or enhancement to existing report?

### Decisions Made

1. **Run/S&P Classification**: "Unknown" is correct for conflicts
2. **Common Information**: Overall Common is useful; Common by band is NOT useful
3. **Multiplier Timeline**: Keep text report, include in bulk download, NOT in dashboards
4. **Multiplier Visualization**: Do NOT pursue at this time

---

## Related Documents

- `DevNotes/Discussions/SWEEPSTAKES_VISUALIZATION_STRATEGY.md` - Detailed discussion and strategy
- `DevNotes/FUTURE_WORK.md` - Committed work items
- `contest_tools/contest_definitions/arrl_ss.json` - Sweepstakes contest definition
