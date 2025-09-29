# Contest Log Analyzer/contest_tools/utils/cty_manager.py
#
# Purpose: Manages the lifecycle of cty.dat files, including on-demand
#          downloading, caching, and indexing from the official source.
#
# Author: Gemini AI
# Date: 2025-09-28
# Version: 0.89.0-Beta
#
# Copyright (c) 2025 Mark Bailey, KD4D
#
# License: Mozilla Public License, v. 2.0
#          (https://www.mozilla.org/MPL/2.0/)
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# TODO: This module uses print() for status messages. This is recognized
#       technical debt and should be migrated to a formal logging system.
#
# --- Revision History ---
## [0.89.0-Beta] - 2025-09-28
# - Initial release of the CtyManager utility.
#
import os
import sys
import json
import zipfile
import datetime
import re
import pathlib
import logging
import requests
from bs4 import BeautifulSoup

class CtyManager:
    """Manages downloading, caching, and finding CTY.DAT files."""

    _INDEX_URL = "https://www.country-files.com/cty/cty.php"
    _INDEX_FILENAME = "cty_index.json"
    _INDEX_MAX_AGE_HOURS = 24

    def __init__(self, root_input_dir: str):
        self.root_input_path = pathlib.Path(root_input_dir)
        self.cty_root_path = self.root_input_path / "data" / "CTY"
        self.zips_path = self.cty_root_path / "zips"
        self.index_path = self.cty_root_path / self._INDEX_FILENAME
        self._setup_directories()
        self.index = self._update_index()

    def _setup_directories(self):
        """Creates the necessary CTY directories if they don't exist."""
        self.cty_root_path.mkdir(parents=True, exist_ok=True)
        self.zips_path.mkdir(exist_ok=True)

    def _is_index_stale(self) -> bool:
        """Checks if the local index file is older than the max age."""
        if not self.index_path.exists():
            return True
        try:
            mod_time = self.index_path.stat().st_mtime
            age = datetime.datetime.now() - datetime.datetime.fromtimestamp(mod_time)
            return age > datetime.timedelta(hours=self._INDEX_MAX_AGE_HOURS)
        except Exception:
            return True

    def _update_index(self) -> list:
        """Updates the local index by scraping the website if the index is stale."""
        if not self._is_index_stale():
            print("INFO: CTY index is up to date.")
            return self._load_index()

        print("INFO: CTY index is stale or missing. Fetching from web...")
        html_content = self._fetch_index_page()
        if not html_content:
            print("ERROR: Could not fetch CTY index page. Using existing local index if available.")
            return self._load_index()

        parsed_data = self._parse_index_page(html_content)
        if parsed_data:
            self._save_index(parsed_data)
            return parsed_data
        else:
            print("ERROR: Failed to parse new CTY data. Using existing local index if available.")
            return self._load_index()

    def _fetch_index_page(self) -> str | None:
        """Fetches the HTML content from the main CTY download page."""
        try:
            response = requests.get(self._INDEX_URL, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not connect to {self._INDEX_URL}: {e}")
            return None

    def _parse_index_page(self, html_content: str) -> list:
        """Parses the HTML to extract CTY file download links and metadata."""
        soup = BeautifulSoup(html_content, 'html.parser')
        data = []
        table = soup.find('table')
        if not table:
            return []
            
        for row in table.find_all('tr')[1:]: # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                try:
                    date_str = cols[0].text.strip()
                    file_link = cols[2].find('a')['href']
                    filename = os.path.basename(file_link)
                    
                    data.append({
                        'date': date_str,
                        'url': file_link,
                        'filename': filename
                    })
                except (AttributeError, KeyError):
                    continue
        return data

    def _load_index(self) -> list:
        """Loads the local CTY index from a JSON file."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                print(f"ERROR: Could not read or parse local index file at {self.index_path}")
        return []

    def _save_index(self, data: list):
        """Saves the CTY index data to a JSON file."""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"INFO: CTY index successfully updated with {len(data)} entries.")
        except IOError:
            print(f"ERROR: Could not write to local index file at {self.index_path}")

    def _download_and_unzip(self, file_info: dict) -> pathlib.Path | None:
        """Downloads and unzips a CTY file, returning the path to the .dat file."""
        zip_path = self.zips_path / file_info['filename']
        
        # Download
        try:
            print(f"INFO: Downloading {file_info['filename']}...")
            response = requests.get(file_info['url'], stream=True, timeout=30)
            response.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Download failed for {file_info['url']}: {e}")
            return None
            
        # Unzip
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                dat_filename = next((name for name in zip_ref.namelist() if name.lower().endswith('.dat')), None)
                if not dat_filename:
                    print(f"ERROR: No .dat file found in {zip_path}")
                    return None
                
                target_path = self.cty_root_path / dat_filename
                zip_ref.extract(dat_filename, self.cty_root_path)
                print(f"INFO: Unzipped to {target_path}")
                return target_path
        except (zipfile.BadZipFile, FileNotFoundError, IOError) as e:
            print(f"ERROR: Failed to unzip {zip_path}: {e}")
            return None

    def find_cty_file_by_name(self, filename: str) -> pathlib.Path | None:
        """Finds a CTY file by its specific filename (e.g., 'cty-3401.dat')."""
        dat_filename = filename if filename.lower().endswith('.dat') else f"{filename}.dat"
        target_path = self.cty_root_path / dat_filename
        if target_path.exists():
            return target_path
        
        zip_filename = dat_filename.replace('.dat', '.zip')
        file_info = next((item for item in self.index if item['filename'] == zip_filename), None)
        
        if file_info:
            return self._download_and_unzip(file_info)
        else:
            print(f"ERROR: Filename '{filename}' not found in the CTY index.")
            return None

    def find_cty_file_by_date(self, contest_date: pd.Timestamp, specifier: str) -> pathlib.Path | None:
        """Finds the most appropriate CTY file based on a contest date."""
        if not self.index:
            print("ERROR: CTY index is empty. Cannot find file by date.")
            return None

        # Convert index dates to datetime objects for comparison
        for item in self.index:
            try:
                # Handle various date formats gracefully
                item['datetime'] = pd.to_datetime(item['date'], errors='coerce').tz_localize('UTC')
            except Exception:
                item['datetime'] = None
        
        valid_entries = [item for item in self.index if item['datetime'] is not None]

        if specifier == 'before':
            # Find the latest file dated on or before the contest
            candidates = [item for item in valid_entries if item['datetime'] <= contest_date]
            if not candidates: return None
            target_entry = max(candidates, key=lambda x: x['datetime'])
        else: # Default to 'after'
            # Find the earliest file dated on or after the contest
            candidates = [item for item in valid_entries if item['datetime'] >= contest_date]
            if not candidates: return None
            target_entry = min(candidates, key=lambda x: x['datetime'])
            
        return self.find_cty_file_by_name(target_entry['filename'])