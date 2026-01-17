# Release Notes: Contest Log Analyzer v1.0.0-alpha.4

**Release Date:** 2026-01-17  
**Branch:** `master`  
**Commits:** 13 commits since v1.0.0-alpha.3

---

## Major Features

### Mode Dimension Support for Single-Band, Multi-Mode Contests
- **ARRL 10 Meter Contest Support** with mode-based activity breakdown
  - QSO Dashboard "Band Activity" tab automatically becomes "Mode Activity" for single-band, multi-mode contests
  - Comparative butterfly chart shows mode breakdown (CW, SSB, etc.) instead of band breakdown
  - Multiplier Dashboard breaks down multipliers by mode instead of by band for single-band contests
  - All six multiplier dashboard tabs (All Multipliers + 5 multiplier types) support mode dimension
- **Dynamic Dimension Detection** based on contest characteristics
  - Automatically detects single-band, multi-mode contests from contest definitions
  - Seamless switching between band and mode dimensions based on contest type
  - Backward compatible with all existing multi-band contests

---

## Enhancements

### Multiplier Dashboard Improvements
- **Unknown (Grey) Legend Added** to multiplier dashboard
  - Top pane legend now includes Run, S&P, and Unknown colors
  - Band Spectrum section includes complete legend (Run, S&P, Unknown)
  - Consistent color coding across all dashboard elements
- **Band Spectrum Legend** added above tab pills
  - Visual legend showing Run, S&P, and Unknown colors
  - Helps users understand color coding in Band Spectrum visualization
- **Dynamic Band Spectrum Tabs** based on multiplier types present
  - Tabs automatically adjust based on contest multiplier rules
  - Supports any number of multiplier types dynamically

### QSO Dashboard Enhancements
- **Adaptive Activity Tab Labeling**
  - "Band Activity" vs "Mode Activity" based on contest type
  - Tab button and card headers update automatically
  - Clear indication of what dimension is being displayed

### Performance and User Experience
- **Raw Data Access Progress Bar** added for better user feedback
  - Visual progress indicator during ZIP file generation
  - Improved user experience during report download
- **QSO Dashboard Performance Improvements**
  - Optimized dashboard loading and rendering

### Contest Definition Enhancements
- **valid_modes Field** added to all contest definitions
  - Enables mode dimension detection across all contests
  - JSON-based mode definitions for consistency
  - Supports future mode-based features

---

## Bug Fixes

### Scoring and Multiplier Fixes
- **Exclude NaN from Multiplier Counting** in standard_calculator
  - Prevents NaN values from being counted as multipliers
  - Ensures accurate multiplier totals and scoring
  - Fixes scoring inconsistencies across reports
- **Scoring Inconsistencies Fixed** in animation reports
  - Removed diagnostic code causing incorrect score display
  - Animation reports now show correct scores

### Dashboard Fixes
- **Multiplier Dashboard Band Spectrum Tabs** made fully dynamic
  - Tabs now properly handle any multiplier type configuration
  - Fixes issues with hardcoded multiplier assumptions
- **QSO Dashboard Mode Labeling** fixed for single-band, multi-mode contests
  - Correct tab labels and headers for ARRL 10 Meter and similar contests
  - Proper mode activity display instead of band activity

### Template and UI Fixes
- **Django Template Syntax Errors** fixed in multiplier dashboard
  - Resolved template tag nesting issues
  - Fixed "else between if/for" template syntax errors
- **Custom Template Filter** added for string manipulation
  - `replace` filter added to analyzer_extras.py for template string operations
  - Proper handling of spaces in filter arguments

---

## Documentation

### User-Facing Documentation Updates
- **All Documentation Updated** to version 1.0.0-alpha.4
  - README.md, UsersGuide.md, ReportInterpretationGuide.md updated
  - Version consistency across all documentation files
- **Mode Dimension Support Documentation** added
  - UsersGuide.md explains mode breakdown for single-band contests
  - ReportInterpretationGuide.md updated with mode activity interpretation
  - Web interface help text updated to reflect adaptive behavior

### Developer Documentation
- **ProgrammersGuide.md Updated** with MultiplierStatsAggregator dimension parameter
  - Documents `get_multiplier_breakdown_data(dimension='band'|'mode')` method
  - Explains automatic dimension detection for single-band, multi-mode contests
- **Technical Debt Documentation** updated
  - Multiplier breakdown reports mode dimension support debt tracked
  - Legacy report compatibility issues documented

### AI Agent Rules
- **Django Template Syntax Rules** added to AI_AGENT_RULES.md
  - Documents template tag nesting constraints
  - Explains "else between if/for" template syntax limitations
  - Provides correct patterns for conditional loops in templates
- **Commit Workflow Rules** for uncommitted files
  - Guidelines for handling untracked files before commits
  - Clear instructions for AI agents on git status checks

### Project Organization
- **File Organization Rules** added
  - Test and temporary scripts location standardized (test_code/)
  - Discussion documents location standardized (DevNotes/)
  - File organization guidelines for AI agents

---

## Technical Details

### Data Aggregation Layer Enhancements
- **MultiplierStatsAggregator.get_multiplier_breakdown_data()** enhanced
  - New `dimension` parameter ('band' or 'mode')
  - Automatic dimension detection based on contest type
  - Returns 'bands' or 'modes' key based on dimension
  - Backward compatible (defaults to 'band')
- **MatrixAggregator** mode dimension support
  - `get_mode_stacked_matrix_data()` for mode-based charts
  - Consistent API with band-based methods

### View and Template Updates
- **multiplier_dashboard view** enhanced for mode dimension
  - Automatic dimension detection from contest definition or JSON structure
  - Splits modes into low_modes_data and high_modes_data for layout (first 3, rest)
  - Handles both fast path (cached JSON) and slow path (regeneration)
- **qso_dashboard view** adaptive labeling
  - Dynamic tab labels and titles based on contest type
  - is_single_band and is_multi_mode detection

---

## Known Issues

### Technical Debt
- **Legacy Report Compatibility** (MEDIUM priority)
  - `text_multiplier_breakdown.py` and `html_multiplier_breakdown.py` still hardcode `data['bands']` key
  - These reports will fail for single-band, multi-mode contests
  - Workaround: Reports work correctly for multi-band contests (default dimension='band')
  - See TECHNICAL_DEBT.md for details and resolution plan

---

## Migration Notes

No migration required. All changes are backward compatible for multi-band contests.

For single-band, multi-mode contests (e.g., ARRL 10 Meter), dashboards will automatically show mode breakdown instead of band breakdown.

---

## Acknowledgments

Special thanks to the amateur radio contesting community for testing and feedback on the ARRL 10 Meter mode dimension support.
