# Contest Log Analyzer/contest_tools/utils/cty_manager.py
#
# Purpose: Manages the lifecycle of cty.dat files, including on-demand
#          downloading, caching, and indexing from the official source.
#
# Author: Gemini AI
# Date: 2025-09-29
# Version: 0.90.1-Beta
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
# --- Revision History ---
## [0.90.1-Beta] - 2025-09-29
### Changed
# - Replaced all `print()` statements with the standard `logging` package
#   to resolve technical debt and align with project standards.
## [0.90.0-Beta] - 2025-09-29
### Changed
# - Changed date comparison logic in `find_cty_file_by_date` to be
#   strictly exclusive (< or >) instead of inclusive (<= or >=).
## [0.89.14-Beta] - 2025-09-29
### Added
# - Added an informational message to confirm which CTY file was selected
#   by date or name.
## [0.89.13-Beta] - 2025-09-29
### Changed
# - Refactored web scraping and indexing logic to match the robust,
#   two-phase (full build/incremental) strategy from the prototype.
# - Replaced incorrect table-based HTML parsing with correct logic that
#   parses <article> tags.
## [0.89.12-Beta] - 2025-09-29
### Changed
# - Rewrote web scraping logic to correctly iterate through paginated
#   yearly archives, matching the user's prototype.
## [0.89.11-Beta] - 2025-09-29
### Changed
# - Rewrote web scraping logic to correctly iterate through paginated
#   yearly archives, matching the user's prototype.
## [0.89.7-Beta] - 2025-09-29
### Fixed
# - Corrected file caching logic in find_cty_file_by_name to check
#   for the file in its year-specific subdirectory before downloading.
## [0.89.6-Beta] - 2025-09-29
### Fixed
# - Corrected filename parsing logic to robustly handle inputs with
#   or without file extensions.
## [0.89.5-Beta] - 2025-09-29
### Fixed
# - Corrected timezone handling logic in find_cty_file_by_date to
#   properly compare timezone-aware and naive datetimes.
## [0.89.4-Beta] - 2025-09-29
### Changed
# - Rewrote the _download_and_unzip method to correctly handle
#   year-based subdirectories and versioned file renaming.
## [0.89.3-Beta] - 2025-09-29
### Fixed
# - Corrected KeyError by making the _download_and_unzip function
#   robust to handle both 'filename' and 'zip_name' keys.
## [0.89.2-Beta] - 2025-09-29
### Fixed
# - Made file lookup logic robust to handle both 'filename' and
#   'zip_name' keys in the cty_index.json file.
## [0.89.1-Beta] - 2025-09-28
### Fixed
# - Added missing 'import pandas as pd' to resolve a NameError.
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
from urllib.parse import urljoin
import pandas as pd
import requests
from bs4 import BeautifulSoup

class CtyManager:
    """Manages downloading, caching, and finding CTY.DAT files."""

    _BASE_URL = "https://www.country-files.com/"
    _INDEX_FILENAME = "cty_index.json"
    _USER_AGENT = "CTYFileFinder/2.1 (Python)"
    _INDEX_MAX_AGE_HOURS = 24

    def __init__(self, root_input_dir: str):
        self.root_input_path = pathlib.Path(root_input_dir)
        self.cty_root_path = self.root_input_path / "data" / "CTY"
        self.zips_path = self.cty_root_path / "zips"
        self.index_path = self.cty_root_path / self._INDEX_FILENAME
        self._setup_directories()
        self.index = self._load_or_update_index()

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

    def _load_or_update_index(self) -> list:
        """Loads the index from cache or updates it by scraping the website."""
        if not self.index_path.exists():
            logging.info("CTY index not found. Performing initial full build...")
            new_index = self._build_full_index()
            if new_index:
                self._save_index(new_index)
                return new_index
            else:
                logging.error("Failed to build initial CTY index.")
                return []

        local_index = self._load_index()
        if self._is_index_stale():
            logging.info("CTY index is stale. Checking for incremental updates...")
            updated_index = self._update_index_incrementally(local_index)
            if len(updated_index) > len(local_index):
                self._save_index(updated_index)
            return updated_index
        else:
            logging.info("CTY index is up to date.")
            return local_index

    def _build_full_index(self) -> list:
        """Performs a one-time, full scrape of the website to build the index."""
        logging.info("Performing initial full build, this may take a moment...")
        headers = {'User-Agent': self._USER_AGENT}
        try:
            response = requests.get(self._BASE_URL, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            archive_widget = soup.select_one('aside#baw_widgetarchives_widget_my_archives-2')
            if not archive_widget:
                logging.error("Could not find the Archives widget for initial build.")
                return []
            year_links = [a['href'] for a in archive_widget.select('li.baw-year > a')]
        except requests.exceptions.RequestException as e:
            logging.error(f"Could not fetch base URL for initial build: {e}")
            return []

        full_index = []
        for year_url in year_links:
            year = year_url.rstrip('/').split('/')[-1]
            logging.info(f"--- Scanning Year: {year} ---")
            page_num = 1
            while True:
                page_url = f"{year_url}page/{page_num}/"
                html_content = self._fetch_index_page(page_url)
                if not html_content: break
                files_on_page = self._parse_archive_page(html_content)
                if not files_on_page: break
                full_index.extend(files_on_page)
                page_num += 1

        full_index.sort(key=lambda x: x['date'], reverse=True)
        return full_index

    def _update_index_incrementally(self, existing_index: list) -> list:
        """Scrapes for files newer than the latest entry in the provided index."""
        if not existing_index:
            return self._build_full_index()

        latest_date_in_index = existing_index[0]['date']
        logging.info(f"Checking for files newer than {latest_date_in_index}...")
        start_year = pd.to_datetime(latest_date_in_index).year
        current_year = datetime.datetime.now().year

        new_files = []
        for year in range(current_year, start_year - 1, -1):
            logging.info(f"--- Checking for updates in {year} ---")
            page_num = 1
            while True:
                page_url = f"{self._BASE_URL}{year}/page/{page_num}/"
                should_stop = False
                html_content = self._fetch_index_page(page_url)
                if not html_content: break
                files_on_page = self._parse_archive_page(html_content)
                if not files_on_page: break

                for file_entry in files_on_page:
                    if file_entry['date'] > latest_date_in_index:
                        new_files.append(file_entry)
                    else:
                        should_stop = True
                        break
                if should_stop: break
                page_num += 1

        if new_files:
            logging.info(f"Found {len(new_files)} new files.")
            updated_index = new_files + existing_index
            updated_index.sort(key=lambda x: x['date'], reverse=True)
            return updated_index
        else:
            logging.info("No new files found. Index is up to date.")
            return existing_index

    def _fetch_index_page(self, url: str) -> str | None:
        """Fetches the HTML content from an archive page."""
        try:
            headers = {'User-Agent': self._USER_AGENT}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 404: return None
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.warning(f"Could not connect to {url} (likely end of pages): {e}")
            return None

    def _parse_archive_page(self, html_content: str) -> list:
        """Parses the HTML of an archive page to extract CTY file metadata."""
        soup = BeautifulSoup(html_content, 'html.parser')
        articles = soup.find_all('article')
        if not articles:
            return []

        data = []
        for article in articles:
            link = article.select_one('a[href*="/cty/download/"][href$=".zip"]')
            time_tag = article.find('time', class_='entry-date')
            if link and time_tag:
                data.append({
                    "date": time_tag['datetime'],
                    "url": urljoin(self._BASE_URL, link['href']),
                    "filename": os.path.basename(link['href'])
                })
        return data

    def _load_index(self) -> list:
        """Loads the local CTY index from a JSON file."""
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logging.error(f"Could not read or parse local index file at {self.index_path}")
        return []

    def _save_index(self, data: list):
        """Saves the CTY index data to a JSON file."""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logging.info(f"CTY index successfully saved with {len(data)} entries.")
        except IOError:
            logging.error(f"Could not write to local index file at {self.index_path}")

    def _download_and_unzip(self, file_info: dict) -> pathlib.Path | None:
        """Downloads and unzips a CTY file, returning the path to the .dat file."""
        zip_filename_str = file_info.get('filename') or file_info.get('zip_name')
        if not zip_filename_str:
            logging.error("CTY index entry is missing a valid filename key.")
            return None

        zip_path = self.zips_path / zip_filename_str
        
        # Download
        try:
            logging.info(f"Downloading {zip_filename_str}...")
            headers = {'User-Agent': self._USER_AGENT}
            response = requests.get(file_info['url'], stream=True, timeout=30, headers=headers)
            response.raise_for_status()
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            logging.error(f"Download failed for {file_info['url']}: {e}")
            return None
            
        # Unzip
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                dat_filename_in_zip = next((name for name in zip_ref.namelist() if name.lower().endswith('.dat')), None)
                if not dat_filename_in_zip:
                    logging.error(f"No .dat file found in {zip_path}")
                    return None
                
                year = pd.to_datetime(file_info['date']).year
                target_dir = self.cty_root_path / str(year)
                target_dir.mkdir(exist_ok=True)

                target_dat_filename = zip_path.stem + ".dat"
                target_path = target_dir / target_dat_filename
                
                # Extract, then rename to the final versioned filename
                extracted_temp_path_str = zip_ref.extract(dat_filename_in_zip, path=target_dir)
                pathlib.Path(extracted_temp_path_str).rename(target_path)

                logging.info(f"Unzipped to {target_path}")
                return target_path
        except (zipfile.BadZipFile, FileNotFoundError, IOError) as e:
            logging.error(f"Failed to unzip {zip_path}: {e}")
            return None

    def find_cty_file_by_name(self, filename: str) -> tuple[pathlib.Path, dict] | tuple[None, None]:
        """Finds a CTY file by its specific filename (e.g., 'cty-3401.dat')."""
        if filename.lower().endswith('.zip'):
            stem = filename[:-4]
        elif filename.lower().endswith('.dat'):
            stem = filename[:-4]
        else:
            stem = filename

        dat_filename = f"{stem}.dat"
        zip_filename = f"{stem}.zip"

        # First, find the file's metadata in the index to determine its year
        file_info = next((item for item in self.index
                          if (item.get('filename') or item.get('zip_name', '')).startswith(stem)), None)

        if not file_info:
            logging.error(f"Filename '{filename}' not found in the CTY index.")
            return None, None

        dat_filename_str = f"{stem}.dat"
        logging.info(f"{dat_filename_str} file selected, Date: {file_info['date']}")

        # Now, construct the full, correct path including the year-based subdirectory
        try:
            year = pd.to_datetime(file_info['date']).year
            target_dir = self.cty_root_path / str(year)
            target_dat_filename = stem + ".dat"
            target_path = target_dir / target_dat_filename
        except Exception as e:
            logging.error(f"Could not parse date or construct path for '{filename}': {e}")
            return None, None

        # Check if the file *already exists* at the correct final destination
        if target_path.exists():
            return target_path, file_info

        if file_info:
            unzipped_path = self._download_and_unzip(file_info)
            return (unzipped_path, file_info) if unzipped_path else (None, None)
        else:
            return None, None

    def find_cty_file_by_date(self, contest_date: pd.Timestamp, specifier: str) -> tuple[pathlib.Path, dict] | tuple[None, None]:
        """Finds the most appropriate CTY file based on a contest date."""
        if not self.index:
            logging.error("CTY index is empty. Cannot find file by date.")
            return None, None

        # Ensure the contest_date is timezone-aware for correct comparison
        if contest_date.tzinfo is None:
            contest_date = contest_date.tz_localize('UTC')

        # Convert index dates to datetime objects for comparison
        for item in self.index:
            try:
                # Handle various date formats gracefully
                dt_aware = pd.to_datetime(item['date'], errors='coerce')
                item['datetime'] = dt_aware.tz_convert('UTC') if dt_aware.tzinfo else dt_aware.tz_localize('UTC')
            except Exception:
                item['datetime'] = None
        
        valid_entries = [item for item in self.index if item['datetime'] is not None]

        if specifier == 'before':
            # Find the latest file dated on or before the contest
            candidates = [item for item in valid_entries if item['datetime'] < contest_date]
            if not candidates: return None, None
            target_entry = max(candidates, key=lambda x: x['datetime'])
        else: # Default to 'after'
            # Find the earliest file dated on or after the contest
            candidates = [item for item in valid_entries if item['datetime'] > contest_date]
            if not candidates: return None, None
            target_entry = min(candidates, key=lambda x: x['datetime'])

        filename_to_find = target_entry.get('filename') or target_entry.get('zip_name')
        return self.find_cty_file_by_name(filename_to_find)