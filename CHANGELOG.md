# Changelog

All notable changes to Contest Log Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - Callsign conversion utilities (`/` → `-` for filenames)
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
