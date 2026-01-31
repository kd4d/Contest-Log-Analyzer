# Changelog

All notable changes to Contest Log Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.0.0-alpha.18] - 2026-01-31
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.18.md)

### Added
- Rate Chart report (QSO or Points rate as grouped bar chart for 1-3 logs); bars touch within hour, vertical grid lines in gaps.
- Bar Graph option in QSO Dashboard Rate Differential pane (toggle with Cumulative Difference).

### Changed
- Contest definitions: single-mode contests now include mode in name (e.g. CQ 160 CW, ARRL SS PH).
- Report drawer and overlay trigger aligned for report navigation.

### Fixed
- Cumulative Difference plots: max 15 horizontal grid lines (shared by both axes); overflow/infinity guarded in axis math.
- Rate Differential pane: Cumulative Difference table no longer truncated; fixed-size + scrollable viewport (same as Band Activity).
- Removed temporary QSO Dashboard diagnostic log messages.

---

## [1.0.0-alpha.17] - 2026-01-30
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.17.md)

### Added
- Report manifest drawer (persistent off-canvas sidebar) on main, QSO, and multiplier dashboards. Pull-out arrow on the left (vertically centered) opens a list of generated reports in the same hierarchy as the ZIP download. Clicking a report opens it in the existing full-screen overlay. List uses actual filenames (callsign/band when present); JSON excluded; undefined reports under Miscellaneous. Search filter, category collapse, active-report highlight, Escape/scrim close.

---

## [1.0.0-alpha.16] - 2026-01-30
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.16.md)

### Fixed
- Multiplier Reports dashboard performance regression: no log load on fast path; reuse contest definition from JSON and session context

### Changed
- Contest name fallback from dashboard context when path extraction fails (multiplier dashboard)

---

## [1.0.0-alpha.15] - 2026-01-30
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.15.md)

### Added
- Rate sheet and comparative rate sheet QSO and Points variants (filenames and dashboard options)
- Cumulative difference plots for Points on points-based contests; QSO Dashboard Rate Differential QSOs/Points toggle
- CQ WPX public log fetcher (CW/SSB); CQ WPX contest option on home page with full dashboard
- Multiplier dashboard hidden for CQ WPX on main dashboard; dedicated "Not available" page for direct WPX multiplier URL

### Changed
- Time series hourly data includes by_band_points / by_mode_points for points-based contests
- Documentation and on-line help updated to v1.0.0-alpha.15; Report Interpretation Guide updated for rate sheet/comparison QSO/Points and cumulative difference Points

---

## [1.0.0-alpha.14] - 2026-01-26
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.14.md)

### Fixed
- Single-log multiplier breakdown reports (Countries/Zones) now display correctly
- Rate Detail tab on QSO Dashboard now works for single logs


## [1.0.0-alpha.13] - 2026-01-26
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.13.md)

### Fixed
- UI visibility improvements - tab labels now much larger and bold for better visibility
- Report layout and display issues - removed unnecessary scrollbars, improved card resizing
- QSO breakdown report alignment - '/' symbols now vertically aligned in all columns
- Report rendering - replaced iframes with direct text rendering in Multiplier Dashboard Analysis Reports

### Added
- InactiveTime column to breakdown reports for better timing analysis
- Zone normalization and CQ 160 mode display improvements

### Changed
- Standardized report filename format and improved error handling
- Updated future work documentation with year-over-year comparison feature

## [1.0.0-alpha.12] - 2026-01-27
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.12.md)

### Fixed
- ARRL DX scoring bug - US/VE station scores were calculated as 2x correct value
  - Fixed StandardCalculator to filter multiplier rules by applies_to field
  - W/VE operators now only count DXCC multipliers (not STPROV)
  - DX operators now only count STPROV multipliers (not DXCC)
- ARRL DX location type determination for Alaska, Hawaii, and US possessions
  - Alaska (KL7), Hawaii (KH6), St. Paul Is. (CY9), and Sable Is. (CY0) now correctly classified as DX stations
  - Consistent location type logic across location resolver and scoring module

### Added
- AI agent operation checklists and maintenance rules documentation

## [1.0.0-alpha.11] - 2026-01-24
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.11.md)

### Added
- Multiplier timeline reports for single-log and multi-log analysis
- Sweepstakes contest-wide QSO breakdown visualization (Phase 1)
- Smart suppression to rate sheet detail sections for single-mode contests
- Mode dimension support to text and HTML multiplier breakdown reports
- Diagnostic logging improvements (elevated to WARNING level)
- Comprehensive documentation versioning policy

### Fixed
- CQ 160 multiplier detection (IG9/IH9 handling and applies_to filter)
- Parser improvements (skip unmatched QSOs and add warning counters)
- ARRL SS CW multiplier dashboard reference line alignment
- QSO chart legend positioning and band distribution migration
- WRTC scoring calculation and UI improvements
- Sweepstakes misleading QSO reports (suppressed and clarified)
- Pandas FutureWarnings and improved error messages
- Docker build optimization (added .dockerignore)

### Changed
- Standardized callsign naming protocol across all file and directory names
- Enhanced Sweepstakes multiplier dashboard and updated supported contests documentation
- Added comprehensive Python cache ignore patterns to .gitignore

## [1.0.0-alpha.10] - 2026-01-20
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.10.md)

### Fixed
- Once per mode multiplier calculation fixes for ARRL 10 Meter and similar contests
  - Fixed Score Summary 'ALL' line to sum multipliers from mode rows instead of union
  - Fixed Breakdown Report totals to use cumulative unique multipliers per mode
  - Fixed Cumulative Multiplier Tracking (CUMM column) to match score summary totals
  - Fixed Multiplier Dashboard "All Multipliers" tab redundancy (hidden when only one multiplier type)
- Dashboard UI improvements - abbreviated multiplier names in tables and tabs
  - Provinces ΓåÆ Provs, Mexican States ΓåÆ Mex, ITU Regions ΓåÆ Regs
  - Reduces space compression in ARRL Analysis Results Dashboard

### Added
- ARRL DX contest support with asymmetric contest rules handling
  - Supports different multipliers for W/VE vs DX entries
  - Multiplier rules filtered by location_type based on entry class
- DevNotes directory reorganization with improved structure
  - New structure: `DevNotes/Archive/`, `DevNotes/Decisions_Architecture/`, `DevNotes/Discussions/`
  - Added `DevNotes/README.md` with organization guidelines
- Template filter for abbreviating multiplier names in UI
- Comprehensive documentation for plugin architecture and testing plans

### Changed
- Enhanced score statistics aggregator for once per mode multiplier calculation
- Improved breakdown report totals calculation for once per mode contests
- Enhanced time series aggregator multiplier tracking per rule per mode
- Improved multiplier dashboard tab display logic

## [1.0.0-alpha.9] - 2026-01-18
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.9.md)

### Fixed
- ARRL 10 Meter multiplier filtering bug - breakdown reports now correctly show multipliers
  - Fixed filtering logic for mutually exclusive multipliers (changed from AND to OR condition)
  - Resolves issue where contests with mutually exclusive multiplier types showed zero multipliers
- Multiplier tracking separation for band vs mode dimensions
  - Fixed issue where multiplier counting was incorrectly mixing band and mode dimensions
  - Ensures accurate multiplier breakdowns for contests with different dimension requirements
- Added missing logger to time series aggregator for multiplier calculation warnings

### Changed
- Enhanced multiplier filtering logic in time series aggregator for mutually exclusive multipliers
  - Updated `_calculate_hourly_multipliers` to use OR logic instead of AND logic
  - Handles contests where each QSO has only one multiplier type populated

### Added
- Comprehensive documentation for mutually exclusive multiplier filtering pattern
  - New file: `DevNotes/MUTUALLY_EXCLUSIVE_MULTIPLIER_FILTERING_PATTERN.md`
  - Documents bug pattern and correct fix pattern for future reference

---

## [1.0.0-alpha.8] - 2026-01-18
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.8.md)

### Added
- CTY file inclusion in download bundle at reports root directory
- Full support for CQ 160 Meter Contest (CW and SSB variants)
- Custom CTY file upload with clear CUSTOM indicator in reports
- Enhanced dashboard score reporting with improved contest definition handling

### Changed
- Dashboard score reports now eliminate cache dependency for contest definitions

---

## [1.0.0-alpha.7] - 2026-01-18
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.7.md)

### Fixed
- File upload regression - form submission now includes files
  - Removed code that disabled file inputs before form submission
  - Disabled file inputs are not included in form data by browsers
  - Only submit buttons are disabled to prevent double-submission
- Release notes CHANGELOG.md path construction
  - Fixed Path object to string conversion for cross-platform compatibility

### Changed
- Diagnostic logging improvements
  - All diagnostics now use WARNING/ERROR level (not INFO)
  - Added comprehensive diagnostic logging for file upload debugging
  - Updated AI Agent Rules to require WARNING/ERROR level for diagnostics

---

## [1.0.0-alpha.6] - 2026-01-17
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.6.md)

### Fixed
- Multiplier Dashboard label capitalization issues
  - "US States" now correctly capitalized (was "Us States")
  - "DXCC CW" now correctly capitalized (was "Dxcc Cw")
  - All multiplier names and modes now properly formatted from contest definitions
- Changed "States" to "US States" in ARRL 10 Meter contest definition
  - Provides clarity when contest has both "US States" and "Mexican States"
  - Ensures consistent naming across all reports and dashboards
- Log Upload/Public Log page double-submission vulnerability
  - Buttons (Upload & Fetch) are now disabled immediately when clicked
  - All form controls are disabled during processing
  - Prevents multiple instances of ingest software from running

### Changed
- Form control state management on upload/fetch operations
  - Form controls are re-enabled if submission fails (client-side errors)
  - Form controls are re-enabled if server returns error (page reload with error)
  - Polling failures now re-enable controls after 5 consecutive errors
  - Users can retry operations without refreshing the page

---

## [1.0.0-alpha.5] - 2026-01-17
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.5.md)

### Added
- Local settings override pattern for production deployments
  - settings.py now imports settings_local.py if it exists (gitignored)
  - Created settings_local.py.example template with production values
  - Production settings persist automatically across updates
  - No more manual stashing/popping of production settings

### Changed
- Configuration management workflow for VPS deployments
  - Production-specific settings (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS) now use override pattern
  - Clean git status on VPS (no modified settings.py)

---

## [1.0.0-alpha.4] - 2026-01-17
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.4.md)

### Added
- Mode dimension support for single-band, multi-mode contests (ARRL 10 Meter)
  - QSO Dashboard "Mode Activity" tab for single-band, multi-mode contests
  - Multiplier Dashboard mode breakdown instead of band breakdown
  - Dynamic dimension detection based on contest characteristics
- Unknown (Grey) legend added to Multiplier Dashboard (top pane and Band Spectrum)
- Band Spectrum legend added above tab pills
- Raw Data Access progress bar for ZIP file generation
- valid_modes field added to all contest definitions

### Changed
- QSO Dashboard "Band Activity" tab automatically becomes "Mode Activity" for single-band contests
- Comparative butterfly chart shows mode breakdown for single-band, multi-mode contests
- Multiplier Dashboard breaks down multipliers by mode for single-band contests
- MultiplierStatsAggregator.get_multiplier_breakdown_data() now supports dimension parameter

### Fixed
- Exclude NaN from multiplier counting in standard_calculator (fixes scoring inconsistencies)
- Scoring inconsistencies fixed in animation reports
- Multiplier Dashboard Band Spectrum tabs made fully dynamic
- QSO Dashboard mode labeling fixed for single-band, multi-mode contests
- Django template syntax errors fixed (else between if/for tags)
- Custom template filter (replace) added for string manipulation

### Documentation
- All documentation updated to version 1.0.0-alpha.4
- Mode dimension support documentation added to UsersGuide.md and ReportInterpretationGuide.md
- ProgrammersGuide.md updated with MultiplierStatsAggregator dimension parameter
- Django Template Syntax Rules added to AI_AGENT_RULES.md
- Technical debt documentation updated for legacy report compatibility

---

## [1.0.0-alpha.3] - 2026-01-16
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md)

### Added
- Release Notes web UI integration
  - New Release Notes page accessible via hamburger menu (renders CHANGELOG.md as HTML)
  - Version badge on About page with link to Release Notes
  - Automatic CHANGELOG.md rendering via web interface
- Markdown library (markdown>=3.4.0) for CHANGELOG.md rendering

### Changed
- Standardized one-line footer format across all reports (Contest Log Analytics v{version}   |   CTY-{version} {date})
- Web dashboard footer abbreviated to "CLA"
- CTY metadata format updated to "CTY-{version} {date}" format
- All text reports now include blank line before footer
- User-facing documentation versioning (all docs now match project version)
- Production URL (cla.kd4d.org) added to user-facing documentation
- CQ WW mode references updated to include RTTY in all documentation

### Fixed
- Missing `get_standard_footer` import in text_continent_breakdown.py

### Documentation
- Comprehensive Release Workflow added to AI_AGENT_RULES.md (includes merge, version bump, release notes, tagging steps)
- Hotfix Workflow Integration documented (emergency release process, version numbering, backporting)
- Rollback Strategy documented (procedures for reverting bad releases)
- CHANGELOG.md workflow documented (Keep a Changelog format, web UI accessibility)
- PDF compatibility restrictions added (no emojis or Unicode symbols in markdown files)
- Emoji removal from documentation (replaced with text equivalents)

---

## [1.0.0-alpha.2] - 2026-01-16
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.2.md)

### Added
- CQ WW RTTY Contest Support
  - Full contest definition with RTTY-specific scoring and multipliers
  - RTTY scoring module (1/2/3 point system)
  - W/VE QTH multiplier resolver with exchange-based resolution
  - Public log fetching support for CQ WW RTTY archives
  - Dynamic band selectors (excludes 160M for RTTY)
- Portable callsign handling
  - Standardized filename format: `{metadata}--{callsigns}.ext`
  - Callsign conversion utilities (`/` ΓåÆ `-` for filenames)
  - Header and QSO line callsign validation

### Changed
- Standardized filename format across all reports
- Dynamic band selectors based on contest `valid_bands`
- Organized ZIP structure in download_all_reports (reports/ and logs/ directories)

### Fixed
- Rate Differential tab data loading (new filename format)
- Interactive animation time display overlay issue
- Multiplier dashboard showing no data in Head to Head tab
- Global QSO rate plot discovery with new filename format
- Cumulative difference plot filename matching
- QSO rate plot filename parsing for new -- delimiter format
- Removed diagnostic beacon code (eliminates 404 warnings)

### Documentation
- Updated Docker installation guide with data files and directory structure
- Added custom dupe checker plugin documentation
- Enhanced contest addition guide with comprehensive information
- Added AI agent rules for strict Angular commit format

---

## [1.0.0-alpha.1] - 2026-01-01
[Full Release Notes](ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.1.md)

### Added
- Initial alpha release
- Core contest log analysis functionality
- Web application interface
- Report generation system
- Multiplier and QSO analysis tools

---
