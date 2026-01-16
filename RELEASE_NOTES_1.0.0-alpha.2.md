# Release Notes: Contest Log Analyzer v1.0.0-alpha.2

**Release Date:** January 16, 2026  
**Branch:** `feature/misc-cleanup-1.0.0-alpha.2`  
**Commits:** 12 commits since v1.0.0-alpha.1

---

## Major Features

### CQ WW RTTY Contest Support
- **Full contest definition** with RTTY-specific scoring and multipliers
- **RTTY scoring module**: 
  - 1 point (same country)
  - 2 points (same continent, different country)
  - 3 points (different continents)
- **W/VE QTH multiplier resolver** with exchange-based resolution
  - All loggers (US/VE/DX) can earn W/VE QTH multipliers
  - Exchange data takes priority over cty.dat
  - AK/HI excluded from W/VE QTH multipliers (country only)
  - Missing QTH flagged as error
- **Public log fetching** support for CQ WW RTTY archives
- **Dynamic band selectors** (excludes 160M for RTTY)
- **Valid bands**: 80M, 40M, 20M, 15M, 10M

### Portable Callsign Handling
- **Standardized filename format**: `{metadata}--{callsigns}.ext`
- **Callsign conversion utilities** (`/` → `-` for filenames)
- **Header and QSO line callsign validation**
- **Backward compatibility** with old filename formats

---

## Enhancements

### QSO Dashboard Improvements
- **Dynamic band selectors** based on contest `valid_bands`
- **Fixed Rate Differential tab** data loading (new filename format)
- **Removed diagnostic beacon code** (eliminates 404 warnings)
- **Fixed interactive animation title** to show all callsigns
- **Fixed time display overlay issue** in animations

### Download & Archive Features
- **Added Cabrillo log files** to download_all_reports ZIP
- **Organized ZIP structure**: `reports/` and `logs/` directories
- **Warning logging** when log files are missing

### UI/UX Improvements
- **Consistent layout** for public log fetch and manual upload sections
- **Fixed QSO rate plot filename parsing**
- **Fixed multiplier dashboard pair detection**

---

## Bug Fixes

- Fixed multiplier dashboard showing no data in Head to Head tab
- Prevented unnecessary log re-ingestion (performance improvement)
- Fixed global QSO rate plot discovery with new filename format
- Fixed interactive animation title display (all callsigns now shown)
- Fixed cumulative difference plot filename matching
- Fixed QSO rate plot filename parsing for new -- delimiter format

---

## Documentation

- Updated Docker installation guide with data files and directory structure
- Added custom dupe checker plugin documentation
- Enhanced contest addition guide with comprehensive information
- Updated README version and fixed documentation links
- Added AI agent rules for strict Angular commit format

---

## Technical Improvements

- Standardized filename format across all reports
- Improved error handling and logging
- Added backward compatibility for filename migrations
- Enhanced validation for callsigns and exchange data
- Updated ARRLDXmults.dat header to document CQ WW RTTY usage

---

## Statistics

- **Files Changed**: 8 files in latest commit
- **Code Changes**: 298 insertions, 114 deletions in latest commit
- **Total Commits**: 12 commits since v1.0.0-alpha.1

---

## Migration Notes

- **Filename format changed** from `{metadata}_{callsigns}.ext` to `{metadata}--{callsigns}.ext`
- System maintains **backward compatibility** with old format
- All views and reports updated to handle both formats during transition

---

## Testing Recommendations

- Verify CQ WW RTTY contest scoring and multipliers
- Test public log fetching for RTTY mode
- Verify band selectors exclude 160M for RTTY contests
- Test download_all_reports includes log files
- Verify portable callsign handling in filenames and URLs
- Test backward compatibility with old filename formats

---

## Deployment

**Ready for deployment to production after testing.**

### Deployment Steps:
1. Pull latest changes: `git pull origin feature/misc-cleanup-1.0.0-alpha.2`
2. Rebuild containers: `docker-compose build`
3. Restart services: `docker-compose up -d`

---

## Commit History

- `d1ca37a` - feat: Enhance CQ WW RTTY support and improve QSO dashboard
- `4dfcc4c` - Add CQ WW RTTY contest support
- `5feef1d` - docs(ai-rules): require strict Angular format for all commits
- `5bbe38f` - docs(readme): update version and fix documentation links
- `a26813a` - Add DevNotes/ to .gitignore
- `1a458b9` - docs(guide): add custom dupe checker plugin documentation
- `7cf9022` - docs(guide): update contest addition guide with comprehensive information
- `f42d070` - Fix multiplier dashboard pair detection and prevent log re-ingestion
- `5c36865` - Fix QSO rate plot filename parsing for new -- delimiter format
- `9aabb21` - Fix interactive animation title to show all callsigns
- `3a9d79a` - Implement portable callsign handling with standardized filename format
- `84ca109` - docs(installation): update Docker installation guide with data files and directory structure details

---

**For questions or issues, please refer to the [Documentation](Docs/) or open an issue on GitHub.**
