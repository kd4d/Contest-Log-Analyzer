# Contest Log Analyzer/contest_tools/contest_definitions/__init__.py
#
# Purpose: Defines the ContestDefinition class, responsible for loading and managing
#          contest-specific rules and mappings from JSON files. It handles merging
#          common Cabrillo field definitions with contest-specific overrides.
#
# Author: Mark Bailey, KD4D
# Contact: kd4d@kd4d.org
# Date: 2025-08-01
# Version: 0.25.0-Beta
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

## [0.25.0-Beta] - 2025-08-01
### Added
# - Added 'contest_period' property to support fixed contest start and end times.

## [0.24.0-Beta] - 2025-08-01
### Added
# - Added 'dupe_check_scope' and 'custom_multiplier_resolver' properties
#   to support contest-specific dupe rules and multiplier logic.

## [0.23.5-Beta] - 2025-08-01
### Fixed
# - Added the missing 'mults_from_zero_point_qsos' property to the class.

## [0.23.4-Beta] - 2025-08-01
### Added
# - Added a 'mults_from_zero_point_qsos' property to support contest-specific
#   scoring rules.

## [0.22.0-Beta] - 2025-07-31
### Added
# - Added an 'excluded_reports' property to allow contest definitions to
#   specify reports that should not be run.

## [0.21.0-Beta] - 2025-07-28
### Removed
# - Removed the 'country_file_name' property as contest-specific country
#   files are no longer used.

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
        self._data = data

    @classmethod
    def _deep_merge_dicts(cls, base: Dict, new: Dict) -> Dict:
        base = copy.deepcopy(base)
        for key, value in new.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = cls._deep_merge_dicts(base[key], value)
            else:
                base[key] = value
        return base

    @classmethod
    def from_json(cls, contest_name: str) -> 'ContestDefinition':
        current_dir = os.path.dirname(os.path.abspath(__file__))
        common_file_path = os.path.join(current_dir, COMMON_CABRILLO_FIELDS_FILE)
        
        base_contest_name = contest_name.rsplit('-', 1)[0].lower().replace('-', '_')
        specific_contest_name = contest_name.lower().replace('-', '_')
        
        specific_file_path = os.path.join(current_dir, f"{specific_contest_name}.json")
        generic_file_path = os.path.join(current_dir, f"{base_contest_name}.json")

        if os.path.exists(specific_file_path):
            contest_file_path = specific_file_path
        elif os.path.exists(generic_file_path):
            contest_file_path = generic_file_path
        else:
            raise FileNotFoundError(f"No definition file found for '{contest_name}' (tried {specific_file_path} and {generic_file_path})")

        with open(common_file_path, 'r', encoding='utf-8') as f:
            common_data = json.load(f)
        with open(contest_file_path, 'r', encoding='utf-8') as f:
            contest_specific_data = json.load(f)

        merged_data = cls._deep_merge_dicts(common_data, contest_specific_data)
        return cls(merged_data)

    @property
    def contest_name(self) -> str:
        return self._data.get('contest_name', 'Unknown Contest')

    @property
    def multiplier_rules(self) -> List[Dict[str, str]]:
        return self._data.get('multiplier_rules', [])

    @property
    def excluded_reports(self) -> List[str]:
        return self._data.get('excluded_reports', [])
        
    @property
    def mults_from_zero_point_qsos(self) -> bool:
        # Defaults to True for backward compatibility with older JSON files
        return self._data.get('mults_from_zero_point_qsos', True)

    @property
    def dupe_check_scope(self) -> str:
        # Defaults to 'per_band' for standard dupe checking
        return self._data.get('dupe_check_scope', 'per_band')

    @property
    def custom_multiplier_resolver(self) -> Optional[str]:
        return self._data.get('custom_multiplier_resolver')

    @property
    def contest_period(self) -> Optional[Dict[str, str]]:
        return self._data.get('contest_period')

    @property
    def cabrillo_version(self) -> str:
        return self._data.get('cabrillo_version', 'Unknown')

    @property
    def header_field_map(self) -> Dict[str, str]:
        return self._data.get('header_field_map', {})

    @property
    def qso_common_fields_regex(self) -> str:
        return self._data.get('qso_common_fields_regex', '')

    @property
    def qso_common_field_names(self) -> list[str]:
        return self._data.get('qso_common_field_names', [])

    @property
    def exchange_parsing_rules(self) -> Dict[str, Dict[str, Any]]:
        return self._data.get('exchange_parsing_rules', {})

    @property
    def default_qso_columns(self) -> list[str]:
        return self._data.get('default_qso_columns', [])

    @property
    def scoring_rules(self) -> Dict[str, Any]:
        return self._data.get('scoring_rules', {})

    def get_exchange_parse_info(self, cabrillo_contest_name: str) -> Optional[Dict[str, Any]]:
        return self.exchange_parsing_rules.get(cabrillo_contest_name)
