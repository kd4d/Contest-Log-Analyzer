# Contest Log Analyzer/contest_tools/contest_definitions/__init__.py
#
# Purpose: Defines the ContestDefinition class, responsible for loading and managing
#          contest-specific rules and mappings from JSON files. It handles merging
#          common Cabrillo field definitions with contest-specific overrides.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-07-25
# Version: 0.15.0-Beta
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
# All notable changes to this project will be documented in this file.
# The format is based on "Keep a Changelog" (https://keepachangelog.com/en/1.0.0/),
# and this project aims to adhere to Semantic Versioning (https://semver.org/).

## [0.15.0-Beta] - 2025-07-25
# - Standardized version for final review. No functional changes.

## [0.13.0-Beta] - 2025-07-22
### Changed
# - Added a 'multiplier_rules' property to read the list of multipliers
#   (e.g., Countries, Zones) from the JSON definition.
# - Added a 'country_file_name' property to read the contest-specific
#   country file (e.g., 'cqww.cty') from the JSON definition.

## [0.10.0-Beta] - 2025-07-21
# - Initial release of the ContestDefinition class.
# - Implemented logic to find specific (e.g., cq_wpx_cw.json) or generic
#   (e.g., cq_wpx.json) contest definition files.

import json
import os
import copy
from typing import Dict, Any, Optional, List

# --- Constants ---
# Name of the common Cabrillo fields JSON file
COMMON_CABRILLO_FIELDS_FILE = '_common_cabrillo_fields.json'

class ContestDefinition:
    """
    Manages and provides access to contest-specific rules and data mappings
    loaded from JSON configuration files. Handles merging common definitions
    with contest-specific overrides.
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Initializes the ContestDefinition with merged data.

        Args:
            data (Dict[str, Any]): A dictionary containing the merged contest definition.
        """
        self._data = data

    @classmethod
    def _deep_merge_dicts(cls, base: Dict, new: Dict) -> Dict:
        """
        Recursively merges two dictionaries. Values from 'new' overwrite values in 'base'.
        If both are dictionaries, merges them recursively.
        """
        base = copy.deepcopy(base)
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = cls._deep_merge_dicts(base[key], value)
            else:
                base[key] = value
        return base

    @classmethod
    def from_json(cls, contest_name: str) -> 'ContestDefinition':
        """
        Loads the ContestDefinition for a given contest name from JSON files.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        common_file_path = os.path.join(current_dir, COMMON_CABRILLO_FIELDS_FILE)
        
        # Handle mode-specific contest names (e.g., CQ-WW-CW)
        # The JSON file might be more generic (e.g., cq_ww.json)
        base_contest_name = contest_name.rsplit('-', 1)[0].lower().replace('-', '_')
        specific_contest_name = contest_name.lower().replace('-', '_')
        
        # Try specific file first, then generic
        specific_file_path = os.path.join(current_dir, f"{specific_contest_name}.json")
        generic_file_path = os.path.join(current_dir, f"{base_contest_name}.json")

        if os.path.exists(specific_file_path):
            contest_file_path = specific_file_path
        elif os.path.exists(generic_file_path):
            contest_file_path = generic_file_path
        else:
            raise FileNotFoundError(f"No definition file found for '{contest_name}' (tried {specific_file_path} and {generic_file_path})")


        try:
            with open(common_file_path, 'r', encoding='utf-8') as f:
                common_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Common Cabrillo fields file not found: {common_file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing common Cabrillo fields JSON: {common_file_path} - {e.msg}", e.doc, e.pos)

        try:
            with open(contest_file_path, 'r', encoding='utf-8') as f:
                contest_specific_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Error parsing contest-specific JSON: {contest_file_path} - {e.msg}", e.doc, e.pos)

        # Merge contest-specific data on top of common data
        merged_data = cls._deep_merge_dicts(common_data, contest_specific_data)

        return cls(merged_data)

    @property
    def contest_name(self) -> str:
        """The official name of the contest (e.g., 'CQ-WPX-CW')."""
        return self._data.get('contest_name', 'Unknown Contest')

    @property
    def country_file_name(self) -> Optional[str]:
        """The specific country file for this contest, if any (e.g., 'cqww.cty')."""
        return self._data.get('country_file_name')

    @property
    def multiplier_rules(self) -> List[Dict[str, str]]:
        """A list of dictionaries defining the multipliers for the contest."""
        return self._data.get('multiplier_rules', [])

    @property
    def cabrillo_version(self) -> str:
        """The Cabrillo version this definition is primarily based on (e.g., '3.0')."""
        return self._data.get('cabrillo_version', 'Unknown')

    @property
    def header_field_map(self) -> Dict[str, str]:
        """Maps Cabrillo header tags (e.g., 'CALLSIGN') to standardized DataFrame column names."""
        return self._data.get('header_field_map', {})

    @property
    def qso_common_fields_regex(self) -> str:
        """Regex pattern to parse the common fields from a QSO line up to the exchange part."""
        return self._data.get('qso_common_fields_regex', '')

    @property
    def qso_common_field_names(self) -> list[str]:
        """List of names for the groups captured by qso_common_fields_regex."""
        return self._data.get('qso_common_field_names', [])

    @property
    def exchange_parsing_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Dictionary of rules for parsing contest-specific exchange fields.
        Keys are contest names, values contain 'regex' and 'groups' for parsing.
        """
        return self._data.get('exchange_parsing_rules', {})

    @property
    def default_qso_columns(self) -> list[str]:
        """A master list of all expected DataFrame column names for QSOs for this contest."""
        return self._data.get('default_qso_columns', [])

    @property
    def scoring_rules(self) -> Dict[str, Any]:
        """Dictionary defining the scoring rules for the contest (points, multipliers, etc.)."""
        return self._data.get('scoring_rules', {})

    def get_exchange_parse_info(self, cabrillo_contest_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the exchange parsing regex and groups for a specific contest name
        as it appears in the Cabrillo CONTEST: line.
        """
        return self.exchange_parsing_rules.get(cabrillo_contest_name)
