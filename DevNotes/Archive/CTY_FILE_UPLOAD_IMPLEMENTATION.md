# CTY File Upload Implementation Discussion

## Current State Analysis

### CTY File Format and Usage

**Verified:** The system currently uses `cty_wt_mod.dat` as the preferred format.

1. **File Naming Convention:**
   - Downloaded zips from country-files.com contain `cty_wt_mod.dat`
   - System renames extracted file to `cty_wt_mod_{version}.dat` (e.g., `cty_wt_mod_3538.dat`)
   - Files stored in: `data/CTY/{year}/cty_wt_mod_{version}.dat`

2. **File Selection:**
   - Currently hardcoded to `'after'` specifier in `_run_analysis_pipeline()`
   - Uses `CtyManager.find_cty_file_by_date()` to select appropriate file
   - CTY file path stored in `ContestLog.cty_dat_path`

3. **Footer Display:**
   - Format: `CTY-{version} {date}` (e.g., "CTY-3538 2024-12-09")
   - Extracts version from filename, date from file header/tag
   - Displayed via `get_cty_metadata()` in `report_utils.py`

### UI Structure

**Current:** Two separate cards on home page:
- **Manual Log Upload** - File input form
- **Public Log Archive** - Dropdown-based log selection

**Question:** Should these be combined?

## UI Design Recommendation

### Recommendation: Keep Separate, but Unify CTY Option

**Rationale:**
1. **Different Mental Models:**
   - Manual Upload = "I have files on my computer"
   - Public Archive = "I want to compare against published logs"
   - These are distinct use cases with different workflows

2. **Progressive Disclosure:**
   - Current separation reduces cognitive load
   - Users don't need to see both options simultaneously
   - Archive section is collapsible (already implemented)

3. **Shared Configuration:**
   - CTY file option should appear in **both** sections
   - Consistent placement and behavior maintains UX cohesion
   - Prevents users from forgetting to configure CTY when switching methods

**Proposed Design:**
```
[Manual Upload Card]
  - Log 1, 2, 3 file inputs (existing)
  - [NEW] CTY File Section:
      ☐ Use Default CTY File (auto-selected based on contest date)
      ○ Upload Custom CTY File: [Browse...]
        Note: Preferred format is cty_wt_mod.dat

[Public Archive Card]
  - Contest/Year/Mode selection (existing)
  - Callsign inputs (existing)
  - [NEW] CTY File Section: (same as above)
```

### Alternative: Radio Button Consolidation (NOT Recommended)

If we combined both methods with radio buttons:
```
○ Upload Files from Computer
○ Select from Public Archive

[Conditional UI based on selection]
```

**Problems:**
- Increases UI complexity (conditional rendering)
- Less discoverable (CTY option might be hidden)
- Harder to maintain (more state management)
- Breaks current clear visual separation

## CTY File Format Requirements

### Standard CTY File Format

The CTY (Country) file format is used by amateur radio software for:
- DXCC entity lookup
- CQ Zone assignment
- ITU Zone assignment
- Continent identification

**Standard Format (`cty_wt_mod.dat`):**
- Line-based format with entity records separated by semicolons
- Each record contains: Country Name, Prefixes, CQ Zone, ITU Zone, Continent, Coordinates, etc.
- May include header comments with version/date: `# RELEASE YYYY.MM.DD`
- May include embedded version tag: `=VERYYYYMMDD`
- Can contain WAE (Worked All Europe) entities

**Parsing Robustness:**
- System already handles missing headers gracefully
- Uses regex patterns to extract version/date when present
- Falls back to "Unknown Date" if header parsing fails

### Custom CTY File Handling

**Challenges:**
1. **Header Validation:**
   - Custom files may have invalid or missing headers
   - Cannot trust embedded dates/versions
   - Must skip header parsing for custom files

2. **Filename Display:**
   - Use original uploaded filename (preserve user's naming)
   - Display as-is in footer (e.g., "my_custom_cty.dat")

3. **Format Validation:**
   - System should validate file is parseable before accepting
   - Allow any `.dat` extension (some users may rename files)
   - Warn if file appears malformed (but don't block processing)

## Implementation Plan

### 1. Form Updates

**Add to `UploadLogForm`:**
```python
cty_file_choice = forms.ChoiceField(
    choices=[('default', 'Use Default CTY File'), ('upload', 'Upload Custom CTY File')],
    initial='default',
    widget=forms.RadioSelect
)
custom_cty_file = forms.FileField(
    required=False,
    widget=forms.FileInput(attrs={'accept': '.dat', 'class': 'form-control'})
)
```

### 2. Backend Processing

**Modify `_run_analysis_pipeline()`:**
- Accept `custom_cty_path` parameter (optional)
- If provided, use directly; otherwise use default `'after'` specifier
- Store custom CTY path in session for bundle inclusion

### 3. CTY Metadata Function

**Update `get_cty_metadata()` in `report_utils.py`:**
```python
# If custom CTY file (check path or flag), return:
# "Custom CTY File: {filename}" instead of "CTY-{version} {date}"
```

### 4. Bundle Inclusion

**Modify `download_all_reports()`:**
- Check for custom CTY file in session
- If present, copy to `logs/` directory in zip bundle
- Use original filename (preserve user's naming)

### 5. Public Archive Support

**Modify fetch form handler:**
- Accept CTY file upload via hidden form field (same as manual)
- Pass to `_run_analysis_pipeline()` identically

## File Format Notes for Users

**Recommended Format:**
- Use `cty_wt_mod.dat` format (standard country-files.com format)
- File should be valid CTY format (semicolon-delimited entity records)
- Any `.dat` extension accepted

**Custom File Limitations:**
- Headers may not be parsed/reliably displayed
- Version information will show as "Custom CTY File"
- Ensure file format matches standard CTY structure for proper parsing

**Why Include in Bundle?**
- Allows reproducing analysis with exact same CTY data
- Important for validation/reproducibility
- Enables offline analysis using downloaded bundle

## Testing Considerations

1. **Default CTY Path:** Verify default selection still works
2. **Custom CTY Upload:** Test with various filenames/extensions
3. **Bundle Creation:** Verify CTY file included in correct location
4. **Footer Display:** Check custom vs default CTY formatting
5. **Error Handling:** Invalid CTY files should fail gracefully
6. **Both Forms:** Manual upload and public archive both support CTY option
