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

## Known Issues

### Score Inconsistency Across Components

**Priority:** HIGH  
**Impact:** User-facing data inconsistency  
**Status:** [ ] In progress

**Description:**
- Text score reports show correct score
- Animation racing bar shows lower score
- Dashboard scoreboard shows wrong score
- All should use same source of truth

**Root Cause:**
- `ScoreStatsAggregator` calculates independently
- `TimeSeriesAggregator` uses calculator plugin output
- They may calculate multipliers differently

**Workaround:**
- Currently use text reports as reference for correct score
- Animation/dashboard scores are incorrect

**Related:**
- See "Scoring Data Source of Truth" in Architecture Debt section

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

**Last Updated:** 2026-01-17  
**Maintained By:** AI Agents and Development Team
