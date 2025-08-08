# Contest Log Analyzer/contest_tools/contest_definitions/__init__.py
#
# Purpose: Defines the ContestDefinition class, which serves as an in-memory
#          representation of a contest's rules and parameters, loaded from
#          a JSON definition file.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-07
# Version: 0.31.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
# --- Revision History ---
## [0.31.0-Beta] - 2025-08-07
# - Initial release of Version 0.31.0-Beta.
import json
import os
from typing import Dict, Any, List

class ContestDefinition:
    """
    Represents the definition of a contest, loaded from a JSON file.
    """
    def __init__(self, data: Dict[str, Any]):
        self.name: str = data.get('name')
        self.dupe_check_scope: str = data.get('dupe_check_scope')
        self.qso_common_fields_regex: str = data.get('qso_common_fields_regex')
        self.qso_common_field_names: List[str] = data.get('qso_common_field_names')
        self.exchange_parsing_rules: Dict[str, Any] = data.get('exchange_parsing_rules')
        self.multiplier_rules: List[Dict[str, Any]] = data.get('multiplier_rules', [])
        self.custom_multiplier_resolver: str = data.get('custom_multiplier_resolver')
        self.operating_time_rules: Dict[str, Any] = data.get('operating_time_rules')
        self.valid_bands: List[str] = data.get('valid_bands', [])
        self.excluded_reports: List[str] = data.get('excluded_reports', [])
        self.contest_specific_event_id_resolver: str = data.get('contest_specific_event_id_resolver')
        self.mults_from_zero_point_qsos: bool = data.get('mults_from_zero_point_qsos', False)
        self.multiplier_report_scope: str = data.get('multiplier_report_scope', 'per_band')

        # --- Load common fields and metrics map ---
        common_fields_path = os.path.join(os.path.dirname(__file__), '_common_cabrillo_fields.json')
        with open(common_fields_path, 'r') as f:
            common_data = json.load(f)
        self.header_field_map: Dict[str, str] = common_data.get('header_field_map', {})
        self.default_qso_columns: List[str] = common_data.get('default_qso_columns', [])
        self.metrics_map: Dict[str, str] = common_data.get('metrics_map', {})

    @classmethod
    def from_json(cls, contest_name: str) -> 'ContestDefinition':
        """
        Loads a contest definition from a JSON file based on the contest name.
        """
        filename = f"{contest_name.lower().replace('-', '_')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not os.path.exists(filepath):
            base_contest_name = contest_name.rsplit('-', 1)[0]
            filename = f"{base_contest_name.lower().replace('-', '_')}.json"
            filepath = os.path.join(os.path.dirname(__file__), filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Contest definition file not found for: {contest_name}")
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        return cls(data)