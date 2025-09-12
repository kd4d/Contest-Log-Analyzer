# Contest Log Analyzer/test_code/test_wae_loader.py
#
# Purpose: A temporary test script to verify the WAE parser, multiplier
#          resolver, and scoring modules during development.
#
# Author: Gemini AI Agent
# Date: 2025-09-12
# Version: 1.0.1-Beta
#
# --- Revision History ---
## [1.0.1-Beta] - 2025-09-12
### Fixed
# - Added sys.path modification to make the script runnable from the
#   project root and resolve ModuleNotFoundError.
#
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
import logging
from Utils.logger_config import setup_logging
from contest_tools.log_manager import LogManager

def main():
    """
    Main function to load a WAE log and print summaries of the
    resulting DataFrames for verification.
    """
    parser = argparse.ArgumentParser(description="WAE Log Loader Test Script")
    parser.add_argument('log_filepath', help="Path to the WAE Cabrillo log file.")
    args = parser.parse_args()

    setup_logging(verbose=True)

    # --- Read and Validate Environment Variables ---
    raw_input_dir = os.environ.get('CONTEST_INPUT_DIR')
    raw_reports_dir = os.environ.get('CONTEST_REPORTS_DIR')

    if not raw_input_dir or not raw_reports_dir:
        logging.error("Required environment variables CONTEST_INPUT_DIR or CONTEST_REPORTS_DIR are not set.")
        sys.exit(1)

    root_input_dir = raw_input_dir.strip().strip('"').strip("'")
    root_reports_dir = raw_reports_dir.strip().strip('"').strip("'")
    
    # Construct the full path to the log file
    full_log_path = os.path.join(root_input_dir, 'Logs', args.log_filepath)

    if not os.path.isfile(full_log_path):
        logging.error(f"Log file not found at: {full_log_path}")
        sys.exit(1)

    logging.info(f"\n--- Loading WAE Log: {args.log_filepath} ---")
    
    try:
        log_manager = LogManager()
        log_manager.load_log(full_log_path, root_input_dir)
        
        if not log_manager.logs:
            logging.error("LogManager failed to load any logs.")
            return
            
        wae_log = log_manager.logs[0]
        
        qsos_df = wae_log.get_processed_data()
        
        # The qtcs_df attribute will be added in a later stage
        qtcs_df = getattr(wae_log, 'qtcs_df', pd.DataFrame())

        print("\n" + "="*50)
        print("                QSO Data Summary")
        print("="*50)
        print(f"Total QSOs Parsed: {len(qsos_df)}")
        if not qsos_df.empty:
            print("Columns: " + ", ".join(qsos_df.columns))
            print("First 5 QSOs:")
            print(qsos_df.head().to_string())
        
        print("\n" + "="*50)
        print("                QTC Data Summary")
        print("="*50)
        print(f"Total QTCs Parsed: {len(qtcs_df)}")
        if not qtcs_df.empty:
            print("Columns: " + ", ".join(qtcs_df.columns))
            print("First 5 QTCs:")
            print(qtcs_df.head().to_string())
            
        logging.info("\n--- Test Load Complete ---")

    except Exception as e:
        logging.error(f"An error occurred during the test load: {e}", exc_info=True)

if __name__ == '__main__':
    # Add pandas to the script for the qtcs_df placeholder
    import pandas as pd
    main()