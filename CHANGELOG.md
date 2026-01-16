# Changelog

All notable changes to Contest Log Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
