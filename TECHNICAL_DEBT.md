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

### StandardCalculator `applies_to` Field Support

**Priority:** HIGH  
**Impact:** Incorrect score calculations for asymmetric contests (e.g., ARRL DX shows 2x multiplier count)  
**Status:** [x] Completed (v1.0.0-alpha.12)

**Issue:**
- `StandardCalculator` (default time-series score calculator) does not respect the `applies_to` field in multiplier rules
- For asymmetric contests like ARRL DX, this causes incorrect multiplier counting
- ARRL DX W/VE operators: Only DXCC multipliers should count, but StandardCalculator counts both DXCC and STPROV (2x multiplier count)
- ARRL DX DX operators: Only STPROV multipliers should count, but StandardCalculator counts both (2x multiplier count)
- Symptom: Plugin calculator shows correct score (30,843,750), StandardCalculator shows exactly half (15,421,875)

**Root Cause:**
- ARRL DX has a contest-specific `scoring_module` (`arrl_dx_scoring`) for point calculation
- ARRL DX does NOT have a `time_series_calculator` defined, so it defaults to `StandardCalculator`
- `StandardCalculator` processes ALL multiplier rules without filtering by `applies_to`
- Other components (`ScoreStatsAggregator`, `MultiplierStatsAggregator`, `TimeSeriesAggregator`) correctly filter by `applies_to`

**Current Workaround:**
- `ScoreStatsAggregator` uses the plugin calculator's score as authoritative (mitigates dashboard score display)
- However, time-series score calculations (used in animations and breakdown reports) still show incorrect values

**Proposed Solution:**
- Add `applies_to` filtering to `StandardCalculator` (similar to other aggregators)
- Filter multiplier rules based on `log_location_type` before processing
- Only process multiplier rules where `applies_to` is None or matches `log_location_type`

**Implementation Pattern:**
```python
# Filter multiplier rules by applies_to (similar to ScoreStatsAggregator)
log_location_type = getattr(log, '_my_location_type', None)
applicable_rules = [
    r for r in contest_def.multiplier_rules 
    if r.get('applies_to') is None or r.get('applies_to') == log_location_type
]
```

**Risk Assessment:**
- **Risk Level:** MEDIUM (potentially breaking change)
- **Affected Contests:** All contests using `StandardCalculator` (ARRL 10, ARRL SS, ARRL FD, CQ WW, CQ WPX, IARU HF, CQ 160, ARRL DX)
- **Mitigation:** Comprehensive regression testing required before implementation

**Testing Strategy:**
- Use `ScoreStatsAggregator` as golden reference (already correctly handles `applies_to`)
- Compare `StandardCalculator` output with `ScoreStatsAggregator` output
- Test all contest patterns: symmetric, asymmetric, different `totaling_method` values
- Regression test all contests using `StandardCalculator`

**Deferral Reason:**
- High risk of breaking changes requires comprehensive regression testing
- Current workaround mitigates dashboard score display issue
- Test plan created, implementation deferred until full regression test suite is ready

**Related:**
- `contest_tools/score_calculators/standard_calculator.py` - File to be updated
- `contest_tools/data_aggregators/score_stats.py` - Reference implementation (lines 168-171)
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_DISCUSSION.md` - Detailed discussion
- `DevNotes/Decisions_Architecture/STANDARD_CALCULATOR_APPLIES_TO_TESTING_PLAN.md` - Testing plan
- `DevNotes/Decisions_Architecture/PLUGIN_ARCHITECTURE_BOUNDARY_DECISION.md` - Architecture principle

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
3. [ ] Add validation to web report generation (CLI deprecated)
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

### WRTC Contest Architecture - Promote to First-Level Contest

**Priority:** MEDIUM  
**Impact:** Cleaner architecture, eliminates special-case logic, better directory structure  
**Status:** [x] Completed (WRTC-2026 implementation)

**Note:** WRTC-2026 implemented as standalone contest. See `DevNotes/WRTC_2026_IMPLEMENTATION_PLAN.md` for details.

**Issue:**
- WRTC is currently implemented as a variant of IARU-HF using inheritance
- Special-case logic in `LogManager`: `--wrtc` flag transforms `IARU-HF` → `WRTC-{year}` at runtime
- Year embedded in contest_name (`WRTC-2026`) instead of being a separate parameter
- Conceptual confusion: WRTC has major differences (scoring, multipliers, reports) but is treated as a variant
- Inheritance misuse: using inheritance for code sharing (parser/exporter) rather than conceptual relationship

**Current Architecture (After Migration):**
```
WRTC-2022 (standalone contest) ✅
WRTC-2026 (standalone contest) ✅
WRTC-2018 (standalone contest) ⏳ (pending implementation)
```

**What WRTC Shares with IARU-HF:**
- Same parser: `iaru_hf_parser` (logs are IARU-HF format)
- Same ADIF exporter: `iaru_hf_adif`
- Same contest period, bands, modes, exchange format
- Same public log archive

**What WRTC Differs:**
- Different scoring: `wrtc_2022_scoring`, `wrtc_2026_scoring` vs `iaru_hf_scoring`
- Different multiplier resolver: `wrtc_multiplier_resolver` vs `iaru_hf_multiplier_resolver`
- Different multiplier rules: DXCC/HQ/Official (no Zones) vs Zones/HQ/Official
- Different reports: `wrtc_propagation`, `wrtc_propagation_animation`
- Year-specific scoring rules (2022/2026: uniform 2/5 points; 2018: TBD)

**Proposed Solution:**
1. Promote WRTC to first-level contest (not a variant of IARU-HF)
2. Use year as a parameter (not in contest_name, not as "overlay")
3. Share parser/exporter via composition (reference, not inheritance)
4. Update directory structure: `reports/{year}/wrtc/{year}/{mode}/...` (year appears twice: contest year and WRTC edition year)
5. Remove `--wrtc` flag transformation logic

**Implementation Approach:**
- Each WRTC year is a standalone contest definition (no base `wrtc.json` inheritance)
- Reference `iaru_hf_parser` and `iaru_hf_adif` via composition (not inheritance)
- Year-specific scoring modules: `wrtc_2022_scoring`, `wrtc_2026_scoring`, `wrtc_2018_scoring` (pending)
- Remove overlay concept entirely - year is just a parameter

**Migration Status:**
- ✅ WRTC-2022: Converted from inheritance to standalone (renamed from 2023)
- ✅ WRTC-2026: Already standalone
- ⏳ WRTC-2018: Pending implementation
- ✅ WRTC-2025: Deleted (does not exist)

**Migration Impact:**
- Existing reports: `reports/2024/wrtc-2026/...` → `reports/2024/wrtc/2026/...`
- Contest name resolution: `WRTC-2026` → `WRTC` with year parameter `2026`
- Backward compatibility: support both patterns during transition

**Estimated Effort:** Medium
- Update JSON definitions
- Refactor LogManager (remove special-case logic)
- Update directory structure code
- Migrate existing reports
- Update tests

**Related:**
- `contest_tools/contest_definitions/wrtc_2022.json` - Standalone WRTC-2022 definition
- `contest_tools/contest_definitions/wrtc_2026.json` - Standalone WRTC-2026 definition
- `contest_tools/contest_definitions/wrtc_2018.json` - Pending implementation
- `DevNotes/WRTC_LEGACY_IMPLEMENTATION_PLAN.md` - Implementation plan for legacy WRTC contests

---

### CQ 160 CW PH Mode Suppression in Breakdown Report

**Priority:** LOW  
**Impact:** PH mode appears in hourly breakdown for CQ 160 CW when it shouldn't  
**Status:** [x] Completed

**Issue:**
- CQ 160 CW contest is CW-only, but hourly breakdown report shows PH (Phone) mode columns
- CQ 160 SSB contest is PH-only, but hourly breakdown report shows CW mode columns
- Contest definition (`cq_160.json`) includes both `["CW", "PH"]` in `valid_modes` to support both variants
- Breakdown report (`text_breakdown_report.py`) used `contest_def.valid_modes` directly without filtering by variant

**Solution Implemented:**
- Updated breakdown report to get modes from actual data (same approach as rate sheet report)
- When dimension is 'mode', extract available modes from `hourly_data.get('by_mode', {}).keys()`
- Only shows modes that actually have data in the log
- Automatically handles both CQ-160-CW (shows only CW) and CQ-160-SSB (shows only PH) variants
- Falls back to contest definition `valid_modes` if no data available

**Changes:**
- `contest_tools/reports/text_breakdown_report.py`: Get modes from actual hourly data instead of contest definition

**Related:**
- `DevNotes/CQ_160_CW_PH_MODE_SUPPRESSION_DISCUSSION.md` - Detailed discussion and solution options
- `contest_tools/reports/text_breakdown_report.py` (line 104) - Mode dimension filtering
- `contest_tools/contest_definitions/cq_160.json` - Contest definition with `valid_modes`
- `contest_tools/contest_specific_annotations/cq_160_parser.py` - Parser extracts variant

---

### Breakdown Report Zero Multipliers (ARRL 10 Meter)

**Priority:** HIGH  
**Impact:** Breakdown report showed zero multipliers for ARRL 10 Meter  
**Status:** [x] Completed

**Issue:**
- Breakdown report (`text_breakdown_report.py`) showed zero multipliers for ARRL 10 Meter contest
- Affected mode dimension breakdown (ARRL 10 is single-band, multi-mode)
- Root cause: Filtering logic used AND instead of OR for mutually exclusive multipliers
- Each QSO has only ONE multiplier column populated (Mult_State, Mult_VE, Mult_XE, Mult_DXCC, or Mult_ITU)
- Filter requiring all columns to be valid removed all rows

**Solution Implemented:**
1. ✅ Fixed filtering logic in `_calculate_hourly_multipliers()` to use OR logic
2. ✅ Filter to rows where ANY multiplier column has valid value, not ALL columns
3. ✅ Separate tracking sets for band vs mode dimensions (independent multiplier counting)
4. ✅ Added missing logger import
5. ✅ Changed diagnostics to WARNING/ERROR level only

**Changes:**
- `contest_tools/data_aggregators/time_series.py`: Fixed filtering logic (line 379-398), separate dimension tracking, added logger import

**Related:**
- `DevNotes/MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md` - Pattern documentation
- `contest_tools/contest_definitions/arrl_10.json` - Mutually exclusive multipliers example

---

### Multiplier Breakdown Reports - Mode Dimension Support

**Priority:** MEDIUM  
**Impact:** Text and HTML multiplier breakdown reports show incorrect dimension for single-band, multi-mode contests  
**Status:** [x] Completed

**Issue:**
- `text_multiplier_breakdown.py` and `html_multiplier_breakdown.py` hardcode `data['bands']` key
- These reports call `get_multiplier_breakdown_data()` without `dimension` parameter (uses default 'band')
- For single-band, multi-mode contests (e.g., ARRL 10 Meter), reports should use `dimension='mode'` to show mode breakdown
- Currently reports show band breakdown (incorrect) instead of mode breakdown (correct) for these contests
- `html_multiplier_breakdown.py` has `if 'bands' in data:` check (line 123) so won't fail, but `text_multiplier_breakdown.py` directly accesses `data['bands']` (line 147)

**Current State:**
- ✅ `json_multiplier_breakdown.py` - Updated to support dimension parameter
- ✅ `multiplier_dashboard` view - Updated to handle both 'bands' and 'modes' keys
- ✅ `text_multiplier_breakdown.py` - Updated to detect dimension and use dynamic key
- ✅ `html_multiplier_breakdown.py` - Updated to detect dimension and use dynamic key

**Solution Implemented:**
1. ✅ Updated `text_multiplier_breakdown.py`:
   - Detects contest type (single-band, multi-mode) using same logic as `json_multiplier_breakdown.py`
   - Passes `dimension` parameter to aggregator
   - Uses dynamic key (`dimension_key = 'modes' if dimension == 'mode' else 'bands'`)
   - Updates section header: "Band Breakdown" → "Mode Breakdown" based on dimension
   - Updates scope label: "All Bands" → "All Modes" based on dimension
2. ✅ Updated `html_multiplier_breakdown.py`:
   - Detects contest type (single-band, multi-mode) using same logic
   - Passes `dimension` parameter to aggregator
   - Uses dynamic key for processing dimension blocks
   - Updates scope label in title lines
   - Handles mode dimension splitting (first half vs second half for modes)

**Resolution:**
- ✅ Both reports now correctly detect single-band, multi-mode contests
- ✅ Reports use mode dimension for ARRL 10 Meter and similar contests
- ✅ Reports use band dimension for multi-band contests (default behavior preserved)
- ✅ All three multiplier breakdown reports (text, HTML, JSON) now consistently support both dimensions

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
