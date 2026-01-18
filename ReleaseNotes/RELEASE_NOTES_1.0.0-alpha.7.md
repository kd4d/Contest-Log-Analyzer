# Release Notes: v1.0.0-alpha.7

**Release Date:** January 18, 2026  
**Tag:** `v1.0.0-alpha.7`

---

## Summary

This release fixes a critical regression in manual file uploads and adds comprehensive diagnostic logging improvements. The file upload form was broken due to disabling file inputs before form submission, preventing files from being included in the POST request.

---

## Fixed

### File Upload Regression
- **Fixed file upload form submission** - Removed code that disabled file inputs before form submission. Disabled file inputs are not included in form data by browsers, causing uploads to fail silently. File inputs are no longer disabled (only submit buttons are disabled to prevent double-submission).

### Diagnostic Logging
- **Enhanced diagnostic logging** - Added comprehensive error-level logging for file upload debugging. All diagnostics now use WARNING or ERROR level to ensure visibility at default log settings.
- **Added diagnostic logging rules** - Updated AI Agent Rules to require WARNING/ERROR level for all diagnostic logging, not INFO level.

### Release Notes
- **Fixed CHANGELOG.md path construction** - Corrected path handling for reading CHANGELOG.md in release notes view (Path object to string conversion for cross-platform compatibility).

---

## Technical Details

### Files Changed
- `web_app/analyzer/templates/analyzer/home.html` - Removed file input disabling from `disableAllFormControls()`
- `web_app/analyzer/views.py` - Added diagnostic logging, fixed CHANGELOG path construction
- `Docs/AI_AGENT_RULES.md` - Added diagnostic logging rules section

### Commits Included
- `fix(upload): prevent file input disabling breaking form submission`

---

## Known Issues

None.

---

## Migration Notes

No migration required. This is a bug fix release.

---

## Next Steps

- Continue testing manual file uploads
- Monitor diagnostic logs for any upload issues

---

**CLA v1.0.0-alpha.7**
