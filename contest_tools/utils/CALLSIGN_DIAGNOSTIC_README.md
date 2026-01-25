# Callsign Diagnostic Utility

## Purpose

This diagnostic utility tracks callsign extraction throughout report generation to identify mismatches between filenames and content.

## How to Enable

Set the environment variable `ENABLE_CALLSIGN_DIAGNOSTIC=true` before running report generation:

```bash
# Windows (PowerShell)
$env:ENABLE_CALLSIGN_DIAGNOSTIC="true"
python main_cli.py --report all <log_files>

# Windows (CMD)
set ENABLE_CALLSIGN_DIAGNOSTIC=true
python main_cli.py --report all <log_files>

# Linux/Mac
export ENABLE_CALLSIGN_DIAGNOSTIC=true
python main_cli.py --report all <log_files>
```

## Output

When enabled, the diagnostic utility:

1. **Logs to Python logger**: All diagnostic events are logged with `[CALLSIGN_DIAG]` prefix
2. **Writes diagnostic file**: `callsign_diagnostic.log` in the report output directory
3. **Reports mismatches**: Summary at end of report generation

## Diagnostic File Format

The diagnostic file contains:
- Report start events (which logs are being processed)
- Filename generation events (callsigns used in filenames)
- Content callsign extraction events (callsigns used in headers/content)
- Cached data callsigns (callsigns found in cached aggregator data)
- Mismatch detections (when filename and content callsigns don't match)

## Example Output

```
================================================================================
REPORT: text_multiplier_breakdown (text)
================================================================================

[2026-01-24T10:30:45] report_start
  report_id: text_multiplier_breakdown
  report_type: text
  logs_count: 3
  callsigns_from_logs: K3LR, W1AW, K5ZD
  log_metadata:
    index: 0
    callsign: K3LR
    contest: CQ-WW-CW
    ...

[2026-01-24T10:30:45] filename_generation
  source: self.logs (sorted all_calls)
  callsigns: K3LR, W1AW, K5ZD
  filename: text_multiplier_breakdown--k3lr_w1aw_k5zd.txt
  context:
    report_id: text_multiplier_breakdown
    logs_count: 3

[2026-01-24T10:30:45] content_callsigns
  source: get_standard_title_lines
  callsigns: K3LR, W1AW, K5ZD
  method: callsigns_override
  context:
    report_name: Multiplier Breakdown (Group Par)
    has_override: True

================================================================================
SUMMARY
================================================================================

Total Reports Processed: 15
Mismatches Detected: 2

MISMATCH DETAILS:

  Report: text_continent_breakdown
    Filename callsigns: K3LR
    Content callsigns: K3LR, W1AW, K5ZD
    In filename but NOT in content: 
    In content but NOT in filename: W1AW, K5ZD
```

## What to Look For

1. **Mismatch Detections**: Any report with mismatches needs investigation
2. **Cached Data Callsigns**: If cached data has more callsigns than `self.logs`, this indicates a pairwise report using cached data with all logs
3. **Source Differences**: Compare `source` fields to see where callsigns are extracted from

## Integration Points

The diagnostic automatically tracks:
- `get_standard_title_lines()` - Content callsign extraction
- `build_callsigns_filename_part()` - Filename callsign extraction
- Report `generate()` methods - When reports start/end
- Cached aggregator data - Callsigns in cached time series data

## Notes

- Diagnostic is disabled by default (no performance impact)
- All diagnostic calls are wrapped in try/except to prevent breaking report generation
- Diagnostic file is written to the same directory as reports for easy access
