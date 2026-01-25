# Callsign Diagnostic Setup Guide

## Overview

The callsign diagnostic utility has been integrated into the report generation system to track and identify mismatches between filenames and content callsigns.

## Files Created/Modified

### New Files
1. `contest_tools/utils/callsign_diagnostic.py` - Diagnostic utility class
2. `contest_tools/utils/CALLSIGN_DIAGNOSTIC_README.md` - Usage documentation

### Modified Files
1. `contest_tools/report_generator.py` - Added diagnostic initialization and hooks
2. `contest_tools/utils/report_utils.py` - Added diagnostic hook to `get_standard_title_lines()`
3. `contest_tools/utils/callsign_utils.py` - Added diagnostic hook to `build_callsigns_filename_part()`
4. `contest_tools/reports/text_continent_breakdown.py` - Added diagnostic logging for filename generation
5. `contest_tools/reports/text_multiplier_breakdown.py` - Added diagnostic logging and `callsigns_override` fix

## How to Run Diagnostic

### For CLI Reports
```bash
# Windows PowerShell
$env:ENABLE_CALLSIGN_DIAGNOSTIC="true"
python main_cli.py --report all <log_files>

# Windows CMD
set ENABLE_CALLSIGN_DIAGNOSTIC=true
python main_cli.py --report all <log_files>

# Linux/Mac
export ENABLE_CALLSIGN_DIAGNOSTIC=true
python main_cli.py --report all <log_files>
```

### For Web Reports (Docker)
```bash
# Set environment variable in docker-compose.yml or docker run command
docker-compose run --rm -e ENABLE_CALLSIGN_DIAGNOSTIC=true web python manage.py <command>
```

### For Regression Tests
Add to test script:
```python
import os
os.environ['ENABLE_CALLSIGN_DIAGNOSTIC'] = 'true'
```

## Diagnostic Output Location

The diagnostic log file is written to:
- **CLI**: `{output_dir}/callsign_diagnostic.log`
- **Web**: `MEDIA_ROOT/sessions/{session_id}/reports/callsign_diagnostic.log`

## What Gets Tracked

1. **Report Start**: Which logs are being processed for each report
2. **Filename Generation**: Callsigns used in filename, source of callsigns
3. **Content Callsigns**: Callsigns extracted for headers/content, method used
4. **Cached Data**: Callsigns found in cached aggregator data
5. **Mismatches**: Automatic detection when filename and content callsigns don't match

## Expected Output

After running with diagnostic enabled, check:
1. **Python logs** (stdout/stderr): Look for `[CALLSIGN_DIAG]` messages
2. **Diagnostic file**: `callsign_diagnostic.log` in report output directory
3. **Summary**: Mismatch count and details at end of file

## Next Steps

1. Run regression tests with diagnostic enabled
2. Review diagnostic log for mismatches
3. Identify patterns in mismatched reports
4. Implement fixes based on actual evidence
5. Re-run tests to verify fixes

## Notes

- Diagnostic is **disabled by default** (no performance impact)
- All diagnostic calls are wrapped in try/except (won't break report generation)
- Diagnostic file is human-readable for easy analysis
