# test_code/verify_engine.py
#
# Purpose: A standalone CLI script to execute the test cases.
#
# Author: Gemini AI
# Date: 2025-12-17
# Version: 0.122.0-Beta
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
#
# --- Revision History ---
# [0.122.0-Beta] - 2025-12-17
# - Initial creation.

import json
import sys
import os
from pathlib import Path

# Add project root to sys.path to allow importing contest_tools
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from contest_tools.data_aggregators.comparative_engine import ComparativeEngine

def run_tests():
    test_file_path = project_root / "test_data" / "engine_test_cases.json"
    
    if not test_file_path.exists():
        print(f"Error: Test data file not found at {test_file_path}")
        sys.exit(1)

    with open(test_file_path, "r") as f:
        data = json.load(f)

    print(f"Running Comparative Engine Verification (Version: {data.get('_version', 'Unknown')})")
    print("-" * 60)

    all_passed = True

    for case in data["test_cases"]:
        name = case["name"]
        inputs = case["inputs"]
        expected = case["expected"]

        # Convert input lists to Sets as required by the engine
        log_multipliers = {k: set(v) for k, v in inputs.items()}

        # Execute Engine
        result = ComparativeEngine.compare_logs(log_multipliers)

        # Verification Logic
        case_passed = True
        errors = []

        # Check Universe
        if result.universe_count != expected["universe_count"]:
            case_passed = False
            errors.append(f"Universe Mismatch: Expected {expected['universe_count']}, Got {result.universe_count}")

        # Check Common
        if result.common_count != expected["common_count"]:
            case_passed = False
            errors.append(f"Common Mismatch: Expected {expected['common_count']}, Got {result.common_count}")

        # Check Station Metrics
        for station, metrics in expected["station_metrics"].items():
            if station not in result.station_metrics:
                case_passed = False
                errors.append(f"Missing Station: {station}")
                continue
            
            actual_metrics = result.station_metrics[station]
            
            if actual_metrics.count != metrics["count"]:
                case_passed = False
                errors.append(f"{station} Count Mismatch: Exp {metrics['count']}, Got {actual_metrics.count}")
            
            if actual_metrics.differential != metrics["differential"]:
                case_passed = False
                errors.append(f"{station} Diff Mismatch: Exp {metrics['differential']}, Got {actual_metrics.differential}")
                
            if actual_metrics.missed != metrics["missed"]:
                case_passed = False
                errors.append(f"{station} Missed Mismatch: Exp {metrics['missed']}, Got {actual_metrics.missed}")

        if case_passed:
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")
            for err in errors:
                print(f"  - {err}")
            all_passed = False

    print("-" * 60)
    if all_passed:
        print("All test cases passed successfully.")
        sys.exit(0)
    else:
        print("Some test cases failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()