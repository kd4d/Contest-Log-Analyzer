# Release Notes: Contest Log Analyzer v1.0.0-alpha.5

**Release Date:** 2026-01-17  
**Branch:** `master`  
**Commits:** 1 commit since v1.0.0-alpha.4

---

## Major Features

### Local Settings Override Pattern for Production
- **Production Settings Persistence** across updates
  - `settings.py` now automatically imports `settings_local.py` if it exists
  - Production-specific settings (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS) persist automatically
  - No more manual stashing/popping of production settings during updates
  - Standard Django pattern for deployment-specific configuration
- **Template File** for easy setup
  - `settings_local.py.example` provides template with production values
  - Copy to `settings_local.py` on VPS for one-time setup
  - File is gitignored and persists across all future updates

---

## Enhancements

### Configuration Management
- **Automatic Settings Override** pattern implemented
  - Production settings no longer conflict with git updates
  - Clean separation between codebase defaults and production overrides
  - Each deployment can have its own `settings_local.py` without conflicts

---

## Technical Details

### Implementation
- Modified `web_app/config/settings.py` to import `settings_local.py` if it exists
- Created `web_app/config/settings_local.py.example` template file
- Added `web_app/config/settings_local.py` to `.gitignore`
- Uses standard Django `try/except ImportError` pattern for optional local settings

### Files Changed
- `web_app/config/settings.py`: Added local settings import
- `web_app/config/settings_local.py.example`: New template file
- `.gitignore`: Added `settings_local.py` to ignore list

---

## Migration Notes

### For VPS/Production Deployments

**One-Time Setup Required:**
1. Pull the latest code: `git pull origin master`
2. Copy the example file: `cp web_app/config/settings_local.py.example web_app/config/settings_local.py`
3. Verify production settings are correct: `cat web_app/config/settings_local.py`
4. Discard old settings.py changes: `git restore web_app/config/settings.py`
5. Rebuild containers: `docker-compose down && docker-compose up --build -d`

**After Setup:**
- `settings_local.py` will persist across all future updates automatically
- No more manual stashing/popping of production settings
- Future updates: just `git pull` and rebuild containers

---

## Benefits

- **Automatic Persistence**: Production settings survive git updates
- **No Conflicts**: Clean git status on VPS (no modified settings.py)
- **Standard Pattern**: Uses well-established Django configuration pattern
- **Flexible**: Each deployment can customize without affecting others
- **Documented**: Example file shows exactly what's needed

---

## Acknowledgments

This change eliminates the manual workflow of stashing and reapplying production settings during updates, making VPS deployments more reliable and maintainable.
