# Release Notes: Contest Log Analyzer v1.0.0-alpha.3

**Release Date:** 2026-01-16  
**Branch:** `master`  
**Commits:** 7 commits since v1.0.0-alpha.2

---

## Major Features

### Release Notes Web UI Integration
- **New Release Notes page** accessible via hamburger menu
  - Renders CHANGELOG.md as HTML using markdown library
  - Styled with Bootstrap for consistent appearance
  - Accessible from Help & Documentation section
- **Version badge on About page** with link to Release Notes
  - Shows current version (e.g., "Version 1.0.0-alpha.3")
  - Clickable badge links to Release Notes page
- **Automatic CHANGELOG.md rendering** via web interface
  - No manual HTML conversion needed
  - Updates automatically when CHANGELOG.md is updated
  - Error handling for missing or unreadable files

---

## Enhancements

### Footer Format Standardization
- **Standardized one-line footer format** across all reports
  - Format: `Contest Log Analytics v{version}   |   CTY-{version} {date}`
  - Web dashboard footer abbreviated to "CLA"
  - Consistent across all text reports and Plotly/HTML reports
- **Blank line before footer** in all text reports
  - Improved readability and visual separation
  - Applied to all 14 text report generators
- **CTY metadata format update**
  - Changed to "CTY-{version} {date}" format (e.g., "CTY-3538 2024-12-09")
  - Removed commit hash from footers (version only)
  - Consistent across all report types

### Documentation Improvements
- **User-facing documentation versioning**
  - All user-facing docs now match project version (1.0.0-alpha.3)
  - UsersGuide.md and InstallationGuide.md versioned
  - README.md version updated
- **Production URL added** to user-facing documentation
  - Added cla.kd4d.org references in README, UsersGuide, InstallationGuide
  - Development (localhost:8000) and production URLs clearly distinguished
- **CQ WW mode references updated** to include RTTY
  - All CQ WW references now mention (CW/SSB/RTTY) or (CW, SSB, or RTTY)
  - Updated in README.md, UsersGuide.md, and web app templates

---

## Bug Fixes

- **Missing import fixed** in `text_continent_breakdown.py`
  - Added missing `get_standard_footer` import
  - Prevents NameError during report generation

---

## Documentation

### Release Workflow Enhancements
- **Comprehensive Release Workflow** added to AI_AGENT_RULES.md
  - Detailed step-by-step process for version releases
  - Includes merge, version bump, release notes, and tagging steps
  - Version numbering guidelines (alpha, beta, rc, release formats)
- **Hotfix Workflow Integration** documented
  - Emergency release process for critical bug fixes
  - Version numbering strategy for hotfixes (patch increment)
  - Backporting guidelines
- **Rollback Strategy** documented
  - Procedures for reverting bad releases
  - Three rollback options (quick revert, tag revert, hotfix)
- **CHANGELOG.md workflow** documented
  - Keep a Changelog format with link to detailed release notes
  - Web UI accessibility noted in workflow
  - Automatic rendering via Release Notes page

### PDF Compatibility
- **PDF compatibility restrictions** added to AI_AGENT_RULES.md
  - All markdown files must be PDF-compatible (no emojis or Unicode symbols)
  - Required for generating PDF documentation
  - Affects all .md files in project
- **Emoji removal** from documentation
  - Replaced emojis with text equivalents ([OK], [X], WARNING:, *)
  - Applied to AI_AGENT_RULES.md, Contributing.md, PerformanceProfilingGuide.md, GitWorkflowSetup.md
  - Prevents LaTeX/PDF conversion errors

---

## Technical Details

### Dependencies
- **Added `markdown>=3.4.0`** to requirements.txt
  - Required for rendering CHANGELOG.md as HTML
  - Extensions: fenced_code, tables, nl2br

### Code Changes
- **New view:** `help_release_notes()` in web_app/analyzer/views.py
  - Reads CHANGELOG.md from project root
  - Converts markdown to HTML with error handling
- **New template:** `help_release_notes.html`
  - Styled changelog display with custom CSS
  - Bootstrap classes for consistent formatting
- **New route:** `help/release-notes/` in web_app/analyzer/urls.py
- **Updated menu:** Added "Release Notes" link to hamburger menu in base.html
- **Updated About page:** Added version badge and Release Notes link

### Version Management
- **Version conflict resolved** in contest_tools/version.py
  - Merge conflict markers removed
  - Kept version 1.0.0-alpha.2 with cross-reference comment
  - Updated to 1.0.0-alpha.3 for this release

---

## Files Changed

**New Files:**
- `web_app/analyzer/templates/analyzer/help_release_notes.html`
- `ReleaseNotes/RELEASE_NOTES_1.0.0-alpha.3.md`

**Modified Files:**
- `contest_tools/version.py` - Updated to 1.0.0-alpha.3
- `contest_tools/utils/report_utils.py` - Standardized footer format
- `contest_tools/templates/base.html` - Added Release Notes menu item
- `contest_tools/reports/text_*.py` (14 files) - Added blank line before footer
- `web_app/analyzer/views.py` - Added help_release_notes view, updated help_about
- `web_app/analyzer/urls.py` - Added release notes route
- `web_app/analyzer/templates/analyzer/about.html` - Added version badges
- `requirements.txt` - Added markdown library
- `README.md` - Updated version, production URL, CQ WW RTTY references
- `Docs/UsersGuide.md` - Updated version, production URL, CQ WW RTTY references
- `Docs/InstallationGuide.md` - Updated version, production URL
- `Docs/AI_AGENT_RULES.md` - Added release workflow, hotfix workflow, rollback strategy, PDF compatibility rules

---

## Migration Notes

No migration required. This is a documentation and UI enhancement release with no breaking changes.

---

## Known Issues

None reported at time of release.

---

## Credits

- Release workflow enhancements based on industry best practices
- Markdown rendering using Python `markdown` library
- Bootstrap styling for consistent UI appearance

---

**Next Release:** TBD (pending feature development)
