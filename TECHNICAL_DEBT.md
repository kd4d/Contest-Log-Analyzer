# Technical Debt Tracking

**Purpose:** Track technical debt items, architectural improvements, and known issues that need attention.

**How to Use:**
- **AI Agents:** Review this document at the start of each session
- **Check off items** as they are completed
- **Add new items** as technical debt is identified
- **Prioritize** items based on impact and effort

**Status Legend:**
- [ ] Not started
- [ ] In progress
- [x] Completed
- ~~[ ] Cancelled/Deprecated~~ (strikethrough)

---

## Architecture & Design Debt

### Scoring Data Source of Truth

**Priority:** HIGH  
**Impact:** Scoring inconsistencies across reports/dashboards  
**Status:** [x] Completed

**Issue:**
- Animation and dashboard show incorrect scores (lower than text reports)
- Text score reports use `ScoreStatsAggregator` (correct)
- Animation/dashboard use `TimeSeriesAggregator` which gets scores from `time_series_score_df` (calculator plugin)
- Calculator (plugin) and aggregator may calculate differently

**Solution Implemented:**
1. ✅ Fixed `standard_calculator` to properly handle `once_per_mode` totaling_method (matches ScoreStatsAggregator logic)
2. ✅ Made `ScoreStatsAggregator` use calculator's final score when available (plugin as authoritative source)
3. ✅ Added validation checks using `ArchitectureValidator` (warns if scores differ)

**Changes:**
- `contest_tools/score_calculators/standard_calculator.py`: Fixed `once_per_mode` handling to count per mode then sum
- `contest_tools/data_aggregators/score_stats.py`: Uses calculator's final score when available, with fallback

**Related:**
- `DevNotes/SCORING_ARCHITECTURE_ANALYSIS.md`
- `DevNotes/SCORING_DATA_SOURCE_OF_TRUTH_ANALYSIS.md`
- `contest_tools/utils/architecture_validator.py`

---

### ARRL 10 Meter Animation File Selection

**Priority:** HIGH  
**Impact:** Animation shows data for only last callsign (alphabetically)  
**Status:** [x] Completed

**Issue:**
- Animation files overwritten because filename based on cached data (all callsigns) not actual logs being processed
- Single-log and multi-log versions used same filename

**Solution:**
- Fixed filename generation to extract callsigns from `self.logs` instead of cached time series data
- Both `_prepare_data_band` and `_prepare_data_mode` now use actual logs

**Related:**
- `DevNotes/ARRL_10_ANIMATION_FILE_SELECTION_ANALYSIS.md`
- `contest_tools/reports/plot_interactive_animation.py` (lines 606, 705)

---

## Validation & Testing Debt

### Architecture Validation Coverage

**Priority:** MEDIUM  
**Impact:** Early detection of architecture violations  
**Status:** [ ] In progress

**Issue:**
- Currently rely on human review to detect architecture violations
- No automated validation for plugin architecture compliance
- No pre-commit hooks for architecture checks

**Solution:**
1. ✅ Created `ArchitectureValidator` utility (Phase 2)
2. ✅ Added validation calls to critical paths (web app report generation pipeline)
3. [ ] Add validation to CLI report generation
4. [ ] Create pre-commit hooks for architecture validation
5. [ ] Add architecture compliance tests

**Related:**
- `contest_tools/utils/architecture_validator.py`
- `web_app/analyzer/views.py` (lines 432-442)
- `DevNotes/ARCHITECTURE_RULE_ENFORCEMENT_DISCUSSION.md`

---

### DAL Pattern Validation

**Priority:** MEDIUM  
**Impact:** Prevent data processing in reports  
**Status:** [ ] Not started

**Issue:**
- No automated detection of DAL violations (manual pivot tables, groupby in reports)
- Currently rely on code review to catch violations

**Solution:**
1. [ ] Add static analysis to detect DAL anti-patterns in reports
2. [ ] Create unit tests that scan report code for violations
3. [ ] Add to pre-commit hooks

**Related:**
- `Docs/AI_AGENT_RULES.md` - DAL Pattern section
- `Docs/ProgrammersGuide.md` - Section 2: DAL

---

## Code Quality Debt

### Python Script Execution Path

**Priority:** LOW  
**Impact:** Consistent Python execution environment  
**Status:** [x] Completed

**Issue:**
- AI agents were using `python` or `python.exe` which didn't work in environment
- Needed explicit path to miniforge Python

**Solution:**
- Added rule to `AI_AGENT_RULES.md` specifying use of `C:\Users\mbdev\miniforge3\python.exe`
- Documented in Python Script Execution Rules section

**Related:**
- `Docs/AI_AGENT_RULES.md` - Python Script Execution Rules

---

## Documentation Debt

### Architecture Rule Enforcement Documentation

**Priority:** HIGH  
**Impact:** Clear guidance for AI agents on architecture  
**Status:** [x] Completed

**Issue:**
- Plugin architecture rules not explicitly documented
- Architecture violations only detected after fact
- No decision framework for architectural changes

**Solution:**
1. ✅ Added "Contest-Specific Plugin Architecture" section to `AI_AGENT_RULES.md`
2. ✅ Added Architecture Decision Framework
3. ✅ Added plugin architecture checklist

**Related:**
- `Docs/AI_AGENT_RULES.md` - Contest-Specific Plugin Architecture section
- `DevNotes/ARCHITECTURE_RULE_ENFORCEMENT_DISCUSSION.md`

---

## Performance Debt

*(No current items)*

---

## Architecture & Design Debt

### CQ 160 CW PH Mode Suppression in Breakdown Report

**Priority:** LOW  
**Impact:** PH mode appears in hourly breakdown for CQ 160 CW when it shouldn't  
**Status:** [ ] Not started

**Issue:**
- CQ 160 CW contest is CW-only, but hourly breakdown report shows PH (Phone) mode columns
- Contest definition (`cq_160.json`) includes both `["CW", "PH"]` in `valid_modes` to support both variants
- Breakdown report (`text_breakdown_report.py`) uses `contest_def.valid_modes` directly without filtering by variant
- Parser extracts specific variant from header (`CQ-160-CW` or `CQ-160-SSB`) but report doesn't use this

**Current State:**
- Parser correctly identifies contest variant (`CQ-160-CW` vs `CQ-160-SSB`)
- Contest definition includes both modes for both variants
- Report displays all modes from definition regardless of actual variant

**Solution:**
- Filter `valid_modes` in breakdown report based on actual contest name from metadata
- If `contest_name == "CQ-160-CW"` → show only CW
- If `contest_name == "CQ-160-SSB"` → show only PH (or SSB depending on mode mapping)

**Related:**
- `DevNotes/CQ_160_CW_PH_MODE_SUPPRESSION_DISCUSSION.md` - Detailed discussion and solution options
- `contest_tools/reports/text_breakdown_report.py` (line 104) - Mode dimension filtering
- `contest_tools/contest_definitions/cq_160.json` - Contest definition with `valid_modes`
- `contest_tools/contest_specific_annotations/cq_160_parser.py` - Parser extracts variant

---

### Multiplier Breakdown Reports - Mode Dimension Support

**Priority:** MEDIUM  
**Impact:** Text and HTML multiplier breakdown reports will fail for single-band, multi-mode contests  
**Status:** [ ] Not started

**Issue:**
- `text_multiplier_breakdown.py` and `html_multiplier_breakdown.py` hardcode `data['bands']` key
- These reports call `get_multiplier_breakdown_data()` without `dimension` parameter (uses default 'band')
- For single-band, multi-mode contests (e.g., ARRL 10 Meter), aggregator returns `'modes'` key instead of `'bands'`
- Reports will raise `KeyError` when accessing `data['bands']` for mode dimension contests

**Current State:**
- ✅ `json_multiplier_breakdown.py` - Updated to support dimension parameter
- ✅ `multiplier_dashboard` view - Updated to handle both 'bands' and 'modes' keys
- ❌ `text_multiplier_breakdown.py` - Hardcodes `data['bands']` (line 147)
- ❌ `html_multiplier_breakdown.py` - Hardcodes `data['bands']` (lines 60, 124)

**Solution:**
1. [ ] Update `text_multiplier_breakdown.py`:
   - Detect contest type (single-band, multi-mode)
   - Pass `dimension` parameter to aggregator
   - Use dynamic key: `data.get('modes', data.get('bands', []))` or detect from structure
   - Update section header: "Band Breakdown" → "Mode Breakdown" or "Band Breakdown" based on dimension
2. [ ] Update `html_multiplier_breakdown.py`:
   - Detect contest type (single-band, multi-mode)
   - Pass `dimension` parameter to aggregator
   - Use dynamic key for splitting bands/modes
   - Update template context to handle both dimensions

**Workaround:**
- Reports will work correctly for multi-band contests (default dimension='band')
- Reports will fail for single-band, multi-mode contests until fixed
- Dashboard uses JSON artifact (which is updated) so dashboard works correctly

**Related:**
- `contest_tools/reports/text_multiplier_breakdown.py` (line 147)
- `contest_tools/reports/html_multiplier_breakdown.py` (lines 60, 124)
- `contest_tools/data_aggregators/multiplier_stats.py` - `get_multiplier_breakdown_data(dimension='band'|'mode')`
- `web_app/analyzer/views.py` - `multiplier_dashboard` view (handles both keys)

---

## Known Issues

### Score Inconsistency Across Components

**Priority:** HIGH  
**Impact:** User-facing data inconsistency  
**Status:** [x] Completed

**Description:**
- ~~Text score reports show correct score~~
- ~~Animation racing bar shows lower score~~
- ~~Dashboard scoreboard shows wrong score~~
- ~~All should use same source of truth~~

**Resolution:**
- ✅ Fixed in "Scoring Data Source of Truth" (Architecture Debt section)
- ✅ Calculator now filters NaN values from multiplier counting
- ✅ ScoreStatsAggregator uses calculator's final score as authoritative source
- ✅ All components now show consistent scores

**Related:**
- See "Scoring Data Source of Truth" in Architecture Debt section (marked as [x] Completed)

---

## Future Enhancements

### Automated Architecture Validation in CI/CD

**Priority:** LOW  
**Impact:** Continuous validation of architecture compliance  
**Status:** [ ] Not started

**Description:**
- Add architecture validation to CI/CD pipeline
- Run `ArchitectureValidator` on all PRs
- Fail builds if critical violations detected

**Related:**
- `contest_tools/utils/architecture_validator.py`
- Pre-commit hooks (future)

---

### AI Agent Self-Validation

**Priority:** LOW  
**Impact:** Prevent architecture violations before code generation  
**Status:** [ ] Not started

**Description:**
- Enhance AI agent behavior to check architecture rules before proposing changes
- Automatically validate architectural compliance in analysis
- Flag potential violations in summaries

**Related:**
- `Docs/AI_AGENT_RULES.md` - Architecture Decision Framework

---

## Notes

- Items are organized by category (Architecture, Validation, Code Quality, Documentation, Performance)
- Priority levels: HIGH, MEDIUM, LOW
- Status indicates current state of work
- Related items link to relevant documents/code
- Check off items as they are completed
- Add new items as technical debt is identified

---

## Technical Debt Incurred (2026-01-17)

### Multiplier Breakdown Dimension Support

**Context:** Added mode dimension support to multiplier dashboard for single-band, multi-mode contests (ARRL 10 Meter).

**Debt Incurred:**

1. **Legacy Report Compatibility:**
   - `text_multiplier_breakdown.py` and `html_multiplier_breakdown.py` still hardcode `data['bands']` key
   - These reports will fail for single-band, multi-mode contests
   - **Mitigation:** Default parameter `dimension='band'` ensures backward compatibility for multi-band contests
   - **Impact:** Medium - affects only single-band, multi-mode contests

2. **JSON Artifact Backward Compatibility:**
   - Old JSON artifacts may have 'bands' key when they should have 'modes' key for single-band, multi-mode contests
   - **Mitigation:** View detects dimension mismatch and regenerates data in slow path
   - **Impact:** Low - automatic regeneration handles this

3. **API Change:**
   - `get_multiplier_breakdown_data()` now accepts optional `dimension` parameter
   - Return structure varies: `'bands'` key vs `'modes'` key
   - **Mitigation:** Default parameter maintains backward compatibility
   - **Impact:** Low - existing code continues to work (defaults to 'band')

**Resolution Plan:**
- See "Multiplier Breakdown Reports - Mode Dimension Support" in Architecture & Design Debt section
- Priority: MEDIUM (reports work for multi-band contests, fail only for single-band, multi-mode)

---

**Last Updated:** 2026-01-17  
**Maintained By:** AI Agents and Development Team
