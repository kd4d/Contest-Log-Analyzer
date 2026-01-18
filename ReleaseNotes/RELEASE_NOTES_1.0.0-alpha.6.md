# Release Notes: Contest Log Analyzer v1.0.0-alpha.6

**Release Date:** 2026-01-17  
**Branch:** `master`  
**Commits:** 2 commits since v1.0.0-alpha.5

---

## Bug Fixes

### Multiplier Dashboard - Label Capitalization
- **Fixed multiplier name capitalization** in Analysis Reports tabs
  - "US States" now correctly capitalized (was "Us States")
  - "DXCC CW" now correctly capitalized (was "Dxcc Cw")
  - "DXCC PH" now correctly capitalized (was "Dxcc Ph")
  - All multiplier names and modes now properly formatted from contest definitions
- **Added `format_multiplier_label()` helper function**
  - Looks up multiplier names from contest definitions (DXCC, US States, etc.)
  - Properly uppercases mode abbreviations (CW, PH, RTTY)
  - Handles abbreviations (DXCC, ITU, US) correctly in fallback formatting
  - Strips mode suffixes from filenames before lookup

### Multiplier Dashboard - Contest Definition
- **Changed "States" to "US States"** in ARRL 10 Meter contest definition
  - Provides clarity when contest has both "US States" and "Mexican States"
  - Ensures consistent naming across all reports and dashboards
  - Updated `contest_tools/contest_definitions/arrl_10.json`

### Log Upload/Public Log Page - Button State Management
- **Fixed double-submission vulnerability**
  - Buttons (Upload & Fetch) are now disabled immediately when clicked
  - All form controls (file inputs, selects, text inputs) are disabled during processing
  - Prevents multiple instances of ingest software from running
- **Added error recovery mechanism**
  - Form controls are re-enabled if submission fails (client-side errors)
  - Form controls are re-enabled if server returns error (page reload with error)
  - Polling failures now re-enable controls after 5 consecutive errors
  - Users can retry operations without refreshing the page

---

## Enhancements

### Multiplier Dashboard
- **Improved label formatting** with contest definition lookup
  - Multiplier names come directly from contest definitions
  - Fallback formatting handles common abbreviations correctly
  - Mode suffixes are properly stripped and uppercased

### User Experience
- **Better error handling** on upload/fetch operations
  - Visual feedback when operations fail
  - Automatic recovery without page refresh
  - Clear error messages for retry scenarios

---

## Technical Details

### Implementation
- Added `format_multiplier_label()` helper in `multiplier_dashboard` view
- Added `disableAllFormControls()` and `enableAllFormControls()` JavaScript functions
- Enhanced error handling in form submission and polling logic
- Updated contest definition for ARRL 10 Meter contest

### Files Changed
- `contest_tools/contest_definitions/arrl_10.json`: Changed "States" to "US States"
- `web_app/analyzer/views.py`: Added multiplier label formatting helper
- `web_app/analyzer/templates/analyzer/home.html`: Added form control disable/enable logic

---

## Migration Notes

### For Users
- No action required
- Existing reports will use new naming ("US States" instead of "States") after regeneration
- Form controls now properly disabled/enabled during operations

### For Developers
- Multiplier names should be defined in contest definitions for consistency
- Use `format_multiplier_label()` for any future multiplier label formatting needs
- Form control state management pattern can be reused for other long-running operations

---

## Known Issues

None at this time.

---

## Next Steps

- Continue testing multiplier dashboard with various contests
- Monitor error recovery mechanisms in production
- Gather feedback on form control state management UX

---

**Full Changelog:** See `CHANGELOG.md` for detailed commit history.
