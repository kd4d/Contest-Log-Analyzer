# contest_tools/utils/callsign_diagnostic.py
#
# Purpose: Diagnostic utility to track callsign extraction and identify mismatches
#          between filenames and content in reports.
#
# Copyright (c) 2025 Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..contest_log import ContestLog

logger = logging.getLogger(__name__)

class CallsignDiagnostic:
    """
    Diagnostic utility to track callsign extraction and identify mismatches.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize diagnostic tracker.
        
        Args:
            output_dir: Optional directory to write diagnostic log file.
                       If None, only logs to Python logger.
        """
        self.output_dir = output_dir
        self.entries: List[Dict[str, Any]] = []
        self.current_report_id: Optional[str] = None
        self.current_report_type: Optional[str] = None
        self.current_logs: Optional[List[ContestLog]] = None
        
    def start_report(self, report_id: str, report_type: str, logs: List[ContestLog]):
        """
        Mark the start of a report generation.
        
        Args:
            report_id: Report identifier
            report_type: Type of report (text, chart, etc.)
            logs: List of ContestLog objects being processed
        """
        self.current_report_id = report_id
        self.current_report_type = report_type
        self.current_logs = logs
        
        # Extract callsigns from logs
        callsigns_from_logs = sorted([
            log.get_metadata().get('MyCall', 'Unknown') 
            for log in logs
        ])
        
        self._log_entry(
            'report_start',
            {
                'report_id': report_id,
                'report_type': report_type,
                'logs_count': len(logs),
                'callsigns_from_logs': callsigns_from_logs,
                'log_metadata': [
                    {
                        'index': i,
                        'callsign': log.get_metadata().get('MyCall', 'Unknown'),
                        'contest': log.get_metadata().get('ContestName', 'Unknown')
                    }
                    for i, log in enumerate(logs)
                ]
            }
        )
    
    def log_filename_generation(self, source: str, callsigns: List[str], filename: str, 
                                context: Optional[Dict[str, Any]] = None):
        """
        Log filename generation with callsigns used.
        
        Args:
            source: Where callsigns came from (e.g., 'self.logs', 'cached_data', 'aggregator')
            callsigns: List of callsigns used in filename
            filename: Generated filename
            context: Optional additional context
        """
        self._log_entry(
            'filename_generation',
            {
                'source': source,
                'callsigns': callsigns,
                'filename': filename,
                'context': context or {}
            }
        )
    
    def log_content_callsigns(self, source: str, callsigns: List[str], 
                              method: str, context: Optional[Dict[str, Any]] = None):
        """
        Log callsigns extracted for content/header generation.
        
        Args:
            source: Where callsigns came from (e.g., 'get_standard_title_lines', 'aggregator')
            callsigns: List of callsigns used in content
            method: Method used to extract (e.g., 'from_logs', 'callsigns_override')
            context: Optional additional context
        """
        self._log_entry(
            'content_callsigns',
            {
                'source': source,
                'callsigns': callsigns,
                'method': method,
                'context': context or {}
            }
        )
    
    def log_cached_data_callsigns(self, data_source: str, callsigns_in_data: List[str],
                                 context: Optional[Dict[str, Any]] = None):
        """
        Log callsigns found in cached aggregator data.
        
        Args:
            data_source: Type of cached data (e.g., 'ts_data', 'matrix_data')
            callsigns_in_data: Callsigns found in the cached data
            context: Optional additional context
        """
        self._log_entry(
            'cached_data_callsigns',
            {
                'data_source': data_source,
                'callsigns_in_data': callsigns_in_data,
                'context': context or {}
            }
        )
    
    def check_mismatch(self, filename_callsigns: List[str], content_callsigns: List[str]) -> bool:
        """
        Check if there's a mismatch between filename and content callsigns.
        
        Args:
            filename_callsigns: Callsigns used in filename
            content_callsigns: Callsigns used in content
            
        Returns:
            True if mismatch detected, False otherwise
        """
        filename_set = set(filename_callsigns)
        content_set = set(content_callsigns)
        
        if filename_set != content_set:
            self._log_entry(
                'mismatch_detected',
                {
                    'filename_callsigns': sorted(filename_callsigns),
                    'content_callsigns': sorted(content_callsigns),
                    'in_filename_not_content': sorted(filename_set - content_set),
                    'in_content_not_filename': sorted(content_set - filename_set)
                }
            )
            return True
        return False
    
    def _log_entry(self, event_type: str, data: Dict[str, Any]):
        """
        Internal method to log diagnostic entries.
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'report_id': self.current_report_id,
            'report_type': self.current_report_type,
            'event_type': event_type,
            'data': data
        }
        self.entries.append(entry)
        
        # Log key events to Python logger for debugging
        # All events are still captured in the diagnostic file
        # Critical diagnostic events are logged at WARNING level to ensure visibility
        if event_type == 'filename_generation':
            # Log filename generation at WARNING level for mismatch diagnosis
            filename = data.get('filename', '[partial]')
            callsigns = data.get('callsigns', [])
            source = data.get('source', 'unknown')
            logger.warning(f"[CALLSIGN_DIAG] filename_generation | Report: {self.current_report_id} | Filename: {filename} | Callsigns: {callsigns} | Source: {source}")
        elif event_type == 'content_callsigns':
            # Log content callsigns extraction at WARNING level for mismatch diagnosis
            callsigns = data.get('callsigns', [])
            source = data.get('source', 'unknown')
            method = data.get('method', 'unknown')
            logger.warning(f"[CALLSIGN_DIAG] content_callsigns | Report: {self.current_report_id} | Source: {source} | Callsigns: {callsigns} | Method: {method}")
        elif event_type == 'cached_data_callsigns':
            # Log cached data callsigns at WARNING level to help diagnose data source issues
            callsigns = data.get('callsigns_in_data', [])
            data_source = data.get('data_source', 'unknown')
            logger.warning(f"[CALLSIGN_DIAG] cached_data_callsigns | Report: {self.current_report_id} | Data Source: {data_source} | Callsigns: {callsigns}")
        elif event_type == 'mismatch_detected':
            # Log mismatches as warnings with detailed information for diagnosis
            filename_calls = data.get('filename_callsigns', [])
            content_calls = data.get('content_callsigns', [])
            in_filename_not_content = data.get('in_filename_not_content', [])
            in_content_not_filename = data.get('in_content_not_filename', [])
            logger.warning(f"[CALLSIGN_DIAG] mismatch_detected | Report: {self.current_report_id} | Filename: {filename_calls} | Content: {content_calls}")
            if in_filename_not_content or in_content_not_filename:
                logger.warning(f"[CALLSIGN_DIAG] mismatch_details | Report: {self.current_report_id} | In filename but NOT in content: {in_filename_not_content} | In content but NOT in filename: {in_content_not_filename}")
        # report_start events are only written to the diagnostic file, not to the Python logger
    
    def finalize_report(self):
        """
        Mark the end of a report generation and check for mismatches.
        
        Only checks entries for the current report_id to avoid cross-report mismatches
        when reports are generated in loops (e.g., single-log reports).
        """
        if not self.entries or not self.current_report_id:
            return
        
        # Find filename and content entries for THIS SPECIFIC REPORT ONLY
        # Filter by current_report_id to avoid comparing entries from different report iterations
        filename_entries = [
            e for e in self.entries 
            if e['event_type'] == 'filename_generation' 
            and e['report_id'] == self.current_report_id
        ]
        content_entries = [
            e for e in self.entries 
            if e['event_type'] == 'content_callsigns'
            and e['report_id'] == self.current_report_id
        ]
        
        if filename_entries and content_entries:
            # Check latest entries for this specific report
            latest_filename = filename_entries[-1]
            latest_content = content_entries[-1]
            
            filename_calls = latest_filename['data'].get('callsigns', [])
            content_calls = latest_content['data'].get('callsigns', [])
            
            self.check_mismatch(filename_calls, content_calls)
    
    def write_diagnostic_file(self, filename: str = "callsign_diagnostic.log"):
        """
        Write all diagnostic entries to a file.
        
        Args:
            filename: Name of diagnostic file
        """
        if not self.output_dir:
            return
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("CALLSIGN DIAGNOSTIC LOG\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write("=" * 80 + "\n\n")
                
                current_report = None
                for entry in self.entries:
                    # Group by report
                    if entry['report_id'] != current_report:
                        current_report = entry['report_id']
                        f.write(f"\n{'=' * 80}\n")
                        f.write(f"REPORT: {current_report} ({entry['report_type']})\n")
                        f.write(f"{'=' * 80}\n\n")
                    
                    # Write entry
                    f.write(f"[{entry['timestamp']}] {entry['event_type']}\n")
                    for key, value in entry['data'].items():
                        if isinstance(value, list):
                            f.write(f"  {key}: {', '.join(map(str, value))}\n")
                        elif isinstance(value, dict):
                            f.write(f"  {key}:\n")
                            for k, v in value.items():
                                f.write(f"    {k}: {v}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                    f.write("\n")
                
                # Summary
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n\n")
                
                mismatch_count = len([e for e in self.entries if e['event_type'] == 'mismatch_detected'])
                f.write(f"Total Reports Processed: {len(set(e['report_id'] for e in self.entries if e['report_id']))}\n")
                f.write(f"Mismatches Detected: {mismatch_count}\n")
                
                if mismatch_count > 0:
                    f.write("\nMISMATCH DETAILS:\n")
                    for entry in self.entries:
                        if entry['event_type'] == 'mismatch_detected':
                            f.write(f"\n  Report: {entry['report_id']}\n")
                            data = entry['data']
                            f.write(f"    Filename callsigns: {', '.join(data.get('filename_callsigns', []))}\n")
                            f.write(f"    Content callsigns: {', '.join(data.get('content_callsigns', []))}\n")
                            if data.get('in_filename_not_content'):
                                f.write(f"    In filename but NOT in content: {', '.join(data['in_filename_not_content'])}\n")
                            if data.get('in_content_not_filename'):
                                f.write(f"    In content but NOT in filename: {', '.join(data['in_content_not_filename'])}\n")
            
            logger.info(f"[CALLSIGN_DIAG] Diagnostic file written: {filepath}")
        except Exception as e:
            logger.error(f"[CALLSIGN_DIAG] Failed to write diagnostic file: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of diagnostic findings.
        
        Returns:
            Dictionary with summary statistics
        """
        unique_reports = set(e['report_id'] for e in self.entries if e['report_id'])
        mismatches = [e for e in self.entries if e['event_type'] == 'mismatch_detected']
        
        return {
            'total_reports': len(unique_reports),
            'total_entries': len(self.entries),
            'mismatches_detected': len(mismatches),
            'mismatch_details': [
                {
                    'report_id': e['report_id'],
                    'data': e['data']
                }
                for e in mismatches
            ]
        }

# Global diagnostic instance (can be set by report generator)
_global_diagnostic: Optional[CallsignDiagnostic] = None

def get_diagnostic() -> Optional[CallsignDiagnostic]:
    """Get the global diagnostic instance."""
    return _global_diagnostic

def set_diagnostic(diagnostic: CallsignDiagnostic):
    """Set the global diagnostic instance."""
    global _global_diagnostic
    _global_diagnostic = diagnostic

def log_filename_generation(source: str, callsigns: List[str], filename: str, 
                           context: Optional[Dict[str, Any]] = None):
    """Convenience function to log filename generation."""
    diag = get_diagnostic()
    if diag:
        diag.log_filename_generation(source, callsigns, filename, context)

def log_content_callsigns(source: str, callsigns: List[str], method: str,
                         context: Optional[Dict[str, Any]] = None):
    """Convenience function to log content callsigns."""
    diag = get_diagnostic()
    if diag:
        diag.log_content_callsigns(source, callsigns, method, context)

def log_cached_data_callsigns(data_source: str, callsigns_in_data: List[str],
                              context: Optional[Dict[str, Any]] = None):
    """Convenience function to log cached data callsigns."""
    diag = get_diagnostic()
    if diag:
        diag.log_cached_data_callsigns(data_source, callsigns_in_data, context)
