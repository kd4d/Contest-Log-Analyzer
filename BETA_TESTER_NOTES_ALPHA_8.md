# Beta Tester Notes: v1.0.0-alpha.7 → v1.0.0-alpha.8

## New Features

### CQ 160 Meter Contest Support
The analyzer now supports the **CQ 160-Meter Contest** for both CW and SSB variants. You can upload CQ 160 logs and get the full suite of analysis reports, including:
- Score summaries with proper multiplier counting (STPROV and DXCC)
- Hourly breakdown reports
- Interactive animations
- Multiplier analysis

**Note:** When uploading CQ 160 logs, the system automatically detects whether it's CW or SSB based on the Cabrillo header.

### Custom CTY File Upload
You can now upload your own CTY (country) file for analysis. This is useful if:
- You're using a custom CTY file with specific DXCC updates
- You want to verify results against a specific CTY version
- You're testing with non-standard country files

**Where to find it:** On the upload page, select "Upload Custom CTY File" in the CTY File section. The uploaded file is clearly marked as "CUSTOM CTY FILE" in all reports.

### CTY File in Download Bundle
When you download all reports as a ZIP file, the CTY file used for analysis is now included at the root of the reports directory. This makes it easier to:
- Verify which CTY version was used for analysis
- Share complete analysis results with others
- Reproduce analysis results later

**Location in bundle:** `reports/YYYY/contest_name/event/calls/cty_file.dat`

## Improvements

### Dashboard Score Reporting
Enhanced score calculation and reporting in the web dashboard for improved accuracy, especially for contests with complex multiplier rules.

## Known Issues

### CQ 160 CW PH Mode in Breakdown Report
For CQ 160 CW contests, the hourly breakdown report may show a PH (Phone) column even though the contest is CW-only. This is a display issue only—the actual scores and analysis are correct. This will be fixed in a future release.

## Testing Focus

Please pay special attention to:

1. **CQ 160 Contest:** Upload both CW and SSB logs and verify:
   - Score calculations are correct
   - Multipliers (STPROV and DXCC) are counted properly
   - Reports generate without errors

2. **Custom CTY Upload:** Test uploading a custom CTY file and verify:
   - Reports show "CUSTOM CTY FILE" indicator
   - Download bundle includes your custom CTY file
   - Multiplier calculations use your custom file correctly

3. **Download Bundle:** After generating reports, download the ZIP and verify:
   - CTY file is present in the reports root directory
   - File matches the one used for analysis

## Questions or Issues?

If you encounter any problems or have questions about these changes, please report them through your usual testing channel.

Thank you for testing!
