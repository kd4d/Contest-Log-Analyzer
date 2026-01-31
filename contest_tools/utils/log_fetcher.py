# contest_tools/utils/log_fetcher.py
#
# Purpose: Scrapes public contest log archives (starting with CQ WW) to provide
#          a searchable index and on-demand file downloading.
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

import requests
from bs4 import BeautifulSoup
import os
import logging
import re
from typing import List, Optional, Dict, Tuple
from .callsign_utils import filename_part_to_callsign

logger = logging.getLogger(__name__)

CQ_WW_BASE_URL = "https://cqww.com/publiclogs/"
CQ_WW_RTTY_BASE_URL = "https://cqwwrtty.com/publiclogs/"

# CQ 160 Public Log Archive
CQ_160_BASE_URL = "https://cq160.com/publiclogs/"

# CQ WPX Public Log Archive (CW and SSB)
CQ_WPX_BASE_URL = "https://cqwpx.com/publiclogs/"

# ARRL Public Log Archive
ARRL_BASE_URL = "https://contests.arrl.org"
ARRL_PUBLICLOGS_URL = f"{ARRL_BASE_URL}/publiclogs.php"

# Mapping: Contest name in our system -> ARRL contest code parameter
ARRL_CONTEST_CODES = {
    'ARRL-10': '10m',
    'ARRL-DX-CW': 'dx',
    'ARRL-DX-SSB': 'dx',
    'ARRL-SS-CW': 'sscw',
    'ARRL-SS-PH': 'ssph',
    'IARU-HF': 'iaruhf',
    # Add other ARRL contests as they're implemented
}

def fetch_log_index(year: str, mode: str) -> List[str]:
    """
    Scrapes the CQ WW public log page for a specific year and mode.
    Returns a list of available callsigns (e.g., ['K3LR', 'KC1XX']).
    """
    # RTTY uses a different domain and URL structure
    if mode == "RTTY":
        target_url = f"{CQ_WW_RTTY_BASE_URL}{year}/"
    else:
        # Construct URL (e.g. 2015ph for SSB, 2015cw for CW)
        mode_suffix = "ph" if mode == "SSB" else "cw"
        target_url = f"{CQ_WW_BASE_URL}{year}{mode_suffix}/"
    
    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Logs are listed as links in a table: <a href='k3lr.log'>K3LR</a>
        # We look for links ending in .log
        links = soup.find_all('a', href=True)
        callsigns = []
        
        for link in links:
            href = link['href']
            if href.endswith('.log'):
                # Extract callsign from filename (k3lr.log -> k3lr, 5b-yt7aw.log -> 5b-yt7aw)
                filename_part = href[:-4].lower()
                # Convert filename part back to callsign format (handles portable callsigns)
                call = filename_part_to_callsign(filename_part)
                callsigns.append(call)
                
        return sorted(list(set(callsigns)))

    except Exception as e:
        logger.error(f"Failed to fetch log index from {target_url}: {e}")
        return []

def download_logs(callsigns: List[str], year: str, mode: str, output_dir: str) -> List[str]:
    """
    Downloads specific log files for the given callsigns into the output directory.
    Returns a list of full paths to the downloaded files.
    """
    # RTTY uses a different domain and URL structure
    if mode == "RTTY":
        base_url = f"{CQ_WW_RTTY_BASE_URL}{year}/"
    else:
        mode_suffix = "ph" if mode == "SSB" else "cw"
        base_url = f"{CQ_WW_BASE_URL}{year}{mode_suffix}/"
    downloaded_paths = []
    
    for call in callsigns:
        filename = f"{call.lower()}.log"
        file_url = f"{base_url}{filename}"
        local_path = os.path.join(output_dir, filename)
        
        try:
            response = requests.get(file_url, timeout=15)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            downloaded_paths.append(local_path)
            logger.info(f"Downloaded: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to download {filename}: {e}")
            
    return downloaded_paths


# ============================================================================
# CQ 160 Public Log Archive Functions
# ============================================================================

def fetch_cq160_log_index(year: str, mode: str) -> List[str]:
    """
    Scrapes the CQ 160 public log page for a specific year and mode.
    Returns a list of available callsigns (e.g., ['K3LR', 'KC1XX']).
    
    Args:
        year: Year as string (e.g., '2024')
        mode: Mode as string ('CW' or 'SSB')
    
    Returns:
        List of callsigns available for download
    """
    # Construct URL (e.g. 2024ph for SSB, 2024cw for CW)
    mode_suffix = "ph" if mode == "SSB" else "cw"
    target_url = f"{CQ_160_BASE_URL}{year}{mode_suffix}/"
    
    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Logs are listed as links in a table: <a href='k3lr.log'>K3LR</a>
        # We look for links ending in .log
        links = soup.find_all('a', href=True)
        callsigns = []
        
        for link in links:
            href = link['href']
            if href.endswith('.log'):
                # Extract callsign from filename (k3lr.log -> k3lr, 5b-yt7aw.log -> 5b-yt7aw)
                filename_part = href[:-4].lower()
                # Convert filename part back to callsign format (handles portable callsigns)
                call = filename_part_to_callsign(filename_part)
                callsigns.append(call)
                
        return sorted(list(set(callsigns)))

    except Exception as e:
        logger.error(f"Failed to fetch CQ 160 log index from {target_url}: {e}")
        return []


def download_cq160_logs(callsigns: List[str], year: str, mode: str, output_dir: str) -> List[str]:
    """
    Downloads specific log files for CQ 160 contest for the given callsigns into the output directory.
    Returns a list of full paths to the downloaded files.
    
    Args:
        callsigns: List of callsigns to download (e.g., ['K3LR', 'KC1XX'])
        year: Year as string (e.g., '2024')
        mode: Mode as string ('CW' or 'SSB')
        output_dir: Directory to save downloaded logs
        
    Returns:
        List of full paths to downloaded log files
    """
    # Construct URL (e.g. 2024ph for SSB, 2024cw for CW)
    mode_suffix = "ph" if mode == "SSB" else "cw"
    base_url = f"{CQ_160_BASE_URL}{year}{mode_suffix}/"
    downloaded_paths = []
    
    for call in callsigns:
        filename = f"{call.lower()}.log"
        file_url = f"{base_url}{filename}"
        local_path = os.path.join(output_dir, filename)
        
        try:
            response = requests.get(file_url, timeout=15)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            downloaded_paths.append(local_path)
            logger.info(f"Downloaded CQ 160 log: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to download CQ 160 log {filename}: {e}")
    
    return downloaded_paths


# ============================================================================
# CQ WPX Public Log Archive Functions
# ============================================================================

def fetch_cqwpx_log_index(year: str, mode: str) -> List[str]:
    """
    Scrapes the CQ WPX public log page for a specific year and mode.
    Returns a list of available callsigns (e.g., ['K3LR', 'KC1XX']).

    CQ WPX public logs: https://cqwpx.com/publiclogs/
    Structure matches CQ WW/CQ 160: {year}ph/ (SSB), {year}cw/ (CW).

    Args:
        year: Year as string (e.g., '2024')
        mode: Mode as string ('CW' or 'SSB')

    Returns:
        List of callsigns available for download
    """
    mode_suffix = "ph" if mode == "SSB" else "cw"
    target_url = f"{CQ_WPX_BASE_URL}{year}{mode_suffix}/"

    try:
        response = requests.get(target_url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        callsigns = []

        for link in links:
            href = link['href']
            if href.endswith('.log'):
                filename_part = href[:-4].lower()
                call = filename_part_to_callsign(filename_part)
                callsigns.append(call)

        return sorted(list(set(callsigns)))

    except Exception as e:
        logger.error(f"Failed to fetch CQ WPX log index from {target_url}: {e}")
        return []


def download_cqwpx_logs(callsigns: List[str], year: str, mode: str, output_dir: str) -> List[str]:
    """
    Downloads specific log files for CQ WPX contest for the given callsigns into the output directory.
    Returns a list of full paths to the downloaded files.

    Args:
        callsigns: List of callsigns to download (e.g., ['K3LR', 'KC1XX'])
        year: Year as string (e.g., '2024')
        mode: Mode as string ('CW' or 'SSB')
        output_dir: Directory to save downloaded logs

    Returns:
        List of full paths to downloaded log files
    """
    mode_suffix = "ph" if mode == "SSB" else "cw"
    base_url = f"{CQ_WPX_BASE_URL}{year}{mode_suffix}/"
    downloaded_paths = []

    for call in callsigns:
        filename = f"{call.lower()}.log"
        file_url = f"{base_url}{filename}"
        local_path = os.path.join(output_dir, filename)

        try:
            response = requests.get(file_url, timeout=15)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                f.write(response.content)

            downloaded_paths.append(local_path)
            logger.info(f"Downloaded CQ WPX log: {filename}")

        except Exception as e:
            logger.error(f"Failed to download CQ WPX log {filename}: {e}")

    return downloaded_paths


# ============================================================================
# ARRL Public Log Archive Functions
# ============================================================================

def _get_arrl_eid_iid(year: str, contest_code: str, contest_name: str = None) -> Optional[Tuple[str, str]]:
    """
    Discovers the event ID (eid) and instance ID (iid) for a given ARRL contest and year.
    
    Scrapes the ARRL public logs selector page to find the year link and extract
    the eid and iid parameters from the href.
    
    Args:
        year: Year as string (e.g., '2024')
        contest_code: ARRL contest code (e.g., '10m', 'dx')
        contest_name: Optional contest name for disambiguation (e.g., 'ARRL-DX-CW', 'ARRL-DX-SSB')
                      Used when contest_code is 'dx' to distinguish between CW and Phone
        
    Returns:
        Tuple of (eid, iid) if found, None otherwise
    """
    try:
        # Load selector page with contest code
        selector_url = f"{ARRL_PUBLICLOGS_URL}?cn={contest_code}"
        response = requests.get(selector_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # For ARRL DX (cn=dx), we need to distinguish between CW and Phone
        # They have different eid values. Try to find the eid from the dropdown or use known values
        if contest_code == 'dx' and contest_name:
            is_cw = 'CW' in contest_name.upper() or contest_name == 'ARRL-DX-CW'
            is_phone = 'SSB' in contest_name.upper() or 'PHONE' in contest_name.upper() or contest_name == 'ARRL-DX-SSB'
            
            # Try to find the eid from the dropdown select options
            # The select has name='eid' and option values are just the eid numbers
            select = soup.find('select', {'name': 'eid'})
            if select:
                for option in select.find_all('option'):
                    option_text = option.get_text().strip().upper()
                    option_value = option.get('value', '')
                    
                    # Check if this option matches our contest
                    # Option values are just numbers like '13' or '14'
                    if is_cw and ('DX CW' in option_text or 'INTERNATIONAL DX CW' in option_text):
                        if option_value and option_value != '0':  # Skip the "Select" option
                            eid_from_option = option_value
                            # Now navigate to that eid page to get year links
                            eid_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid_from_option}"
                            response = requests.get(eid_url, timeout=10)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.text, 'html.parser')
                            break
                    elif is_phone and ('DX PHONE' in option_text or 'INTERNATIONAL DX PHONE' in option_text):
                        if option_value and option_value != '0':  # Skip the "Select" option
                            eid_from_option = option_value
                            eid_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid_from_option}"
                            response = requests.get(eid_url, timeout=10)
                            response.raise_for_status()
                            soup = BeautifulSoup(response.text, 'html.parser')
                            break
        
        # Find year links - they appear as links with year text
        year_links = soup.find_all('a', href=True, string=re.compile(rf'^{year}$'))
        
        for link in year_links:
            href = link.get('href', '')
            # Extract eid and iid from href like "publiclogs.php?eid=21&iid=1073"
            match = re.search(r'eid=(\d+)&iid=(\d+)', href)
            if match:
                eid, iid = match.groups()
                logger.info(f"Found ARRL eid={eid}, iid={iid} for {contest_code} {year} (contest_name={contest_name})")
                return (eid, iid)
        
        logger.warning(f"Could not find eid/iid for ARRL {contest_code} {year} (contest_name={contest_name})")
        return None
        
    except Exception as e:
        logger.error(f"Failed to get ARRL eid/iid for {contest_code} {year} (contest_name={contest_name}): {e}")
        return None


def fetch_arrl_log_index(year: str, contest_code: str, contest_name: str = None) -> List[str]:
    """
    Fetches list of available callsigns for an ARRL contest and year.
    
    Scrapes the ARRL public logs listing page to extract callsigns from the table.
    Returns only the callsigns (not the q parameters needed for downloads).
    
    Args:
        year: Year as string (e.g., '2024')
        contest_code: ARRL contest code (e.g., '10m', 'dx')
        contest_name: Optional contest name for disambiguation (e.g., 'ARRL-DX-CW', 'ARRL-DX-SSB')
                      Used when contest_code is 'dx' to distinguish between CW and Phone
        
    Returns:
        List of callsigns in sorted order (e.g., ['2E0BLN', 'K3LR'])
    """
    try:
        # Get event/instance IDs
        eid_iid = _get_arrl_eid_iid(year, contest_code, contest_name=contest_name)
        if not eid_iid:
            logger.error(f"Could not get eid/iid for ARRL {contest_code} {year} (contest_name={contest_name})")
            return []
        
        eid, iid = eid_iid
        
        # Load log listing page
        listing_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid}&iid={iid}"
        response = requests.get(listing_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table containing log listings
        table = soup.find('table')
        if not table:
            logger.warning(f"No table found on ARRL log listing page for {contest_code} {year}")
            return []
        
        # Extract callsigns from table links
        callsigns = []
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                link = cell.find('a')
                if link:
                    callsign = link.text.strip()
                    if callsign:
                        callsigns.append(callsign.upper())
        
        return sorted(list(set(callsigns)))
        
    except Exception as e:
        logger.error(f"Failed to fetch ARRL log index for {contest_code} {year}: {e}")
        return []


def fetch_arrl_log_mapping(year: str, contest_code: str, contest_name: str = None) -> Dict[str, str]:
    """
    Fetches mapping of callsign -> encoded q parameter for ARRL logs.
    
    This mapping is required for downloading logs, as the q parameter
    cannot be constructed - it must be scraped from the log listing table.
    
    Args:
        year: Year as string (e.g., '2024')
        contest_code: ARRL contest code (e.g., '10m', 'dx')
        contest_name: Optional contest name for disambiguation (e.g., 'ARRL-DX-CW', 'ARRL-DX-SSB')
                      Used when contest_code is 'dx' to distinguish between CW and Phone
        
    Returns:
        Dictionary mapping callsign (uppercase) -> q parameter
    """
    try:
        # Get event/instance IDs
        eid_iid = _get_arrl_eid_iid(year, contest_code, contest_name=contest_name)
        if not eid_iid:
            logger.error(f"Could not get eid/iid for ARRL {contest_code} {year} (contest_name={contest_name})")
            return {}
        
        eid, iid = eid_iid
        
        # Load log listing page
        listing_url = f"{ARRL_PUBLICLOGS_URL}?eid={eid}&iid={iid}"
        response = requests.get(listing_url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table containing log listings
        table = soup.find('table')
        if not table:
            logger.warning(f"No table found on ARRL log listing page for {contest_code} {year}")
            return {}
        
        # Extract callsign -> q parameter mapping from table links
        mapping = {}
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                link = cell.find('a', href=True)
                if link:
                    callsign = link.text.strip().upper()
                    href = link.get('href', '')
                    
                    # Extract q parameter from href: "showpubliclog.php?q=<encoded>"
                    if 'showpubliclog.php?q=' in href:
                        q_param = href.split('q=', 1)[1]
                        mapping[callsign] = q_param
                    else:
                        logger.warning(f"Unexpected href format for callsign {callsign}: {href}")
        
        logger.info(f"Fetched ARRL log mapping: {len(mapping)} callsigns for {contest_code} {year}")
        return mapping
        
    except Exception as e:
        logger.error(f"Failed to fetch ARRL log mapping for {contest_code} {year}: {e}")
        return {}


def download_arrl_logs(callsigns: List[str], year: str, contest_code: str, output_dir: str, contest_name: str = None) -> List[str]:
    """
    Downloads specific log files for an ARRL contest.
    
    Uses the showpubliclog.php endpoint with encoded q parameters that are
    scraped from the log listing table (cannot be constructed).
    
    Args:
        callsigns: List of callsigns to download (e.g., ['2E0BLN', 'K3LR'])
        year: Year as string (e.g., '2024')
        contest_code: ARRL contest code (e.g., '10m', 'dx')
        output_dir: Directory to save downloaded logs
        contest_name: Optional contest name for disambiguation (e.g., 'ARRL-DX-CW', 'ARRL-DX-SSB')
                      Used when contest_code is 'dx' to distinguish between CW and Phone
        
    Returns:
        List of full paths to downloaded log files
    """
    try:
        # Fetch the callsign -> q parameter mapping
        mapping = fetch_arrl_log_mapping(year, contest_code, contest_name=contest_name)
        if not mapping:
            logger.error(f"Could not get log mapping for ARRL {contest_code} {year} (contest_name={contest_name})")
            return []
        
        downloaded_paths = []
        
        for call in callsigns:
            call_upper = call.upper()
            q_param = mapping.get(call_upper)
            
            if not q_param:
                logger.warning(f"No q parameter found for callsign {call} in ARRL {contest_code} {year}")
                continue
            
            # Construct download URL: showpubliclog.php?q=<encoded>
            file_url = f"{ARRL_BASE_URL}/showpubliclog.php?q={q_param}"
            local_path = os.path.join(output_dir, f"{call.lower()}.log")
            
            try:
                response = requests.get(file_url, timeout=15)
                response.raise_for_status()
                
                # Verify it's actually a log file (contains CABRILLO or START-OF-LOG)
                content_preview = response.text[:100].upper()
                if 'CABRILLO' not in content_preview and 'START-OF-LOG' not in content_preview:
                    logger.warning(f"Downloaded file for {call} doesn't appear to be a Cabrillo log")
                
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_paths.append(local_path)
                logger.info(f"Downloaded ARRL log: {call}.log")
                
            except Exception as e:
                logger.error(f"Failed to download ARRL log for {call}: {e}")
        
        return downloaded_paths
        
    except Exception as e:
        logger.error(f"Failed to download ARRL logs for {contest_code} {year}: {e}")
        return []


# ============================================================================
# IARU HF Public Log Archive Functions (uses same archive as ARRL)
# ============================================================================

def fetch_iaru_log_index(year: str) -> List[str]:
    """
    Fetches list of available callsigns for IARU HF contest and year.
    
    IARU HF uses the same ARRL public log archive structure.
    
    Args:
        year: Year as string (e.g., '2024')
        
    Returns:
        List of callsigns in sorted order (e.g., ['2E0BLN', 'K3LR'])
    """
    return fetch_arrl_log_index(year, 'iaruhf', contest_name='IARU-HF')


def download_iaru_logs(callsigns: List[str], year: str, output_dir: str) -> List[str]:
    """
    Downloads specific log files for IARU HF contest.
    
    IARU HF uses the same ARRL public log archive structure.
    
    Args:
        callsigns: List of callsigns to download (e.g., ['2E0BLN', 'K3LR'])
        year: Year as string (e.g., '2024')
        output_dir: Directory to save downloaded logs
        
    Returns:
        List of full paths to downloaded log files
    """
    return download_arrl_logs(callsigns, year, 'iaruhf', output_dir, contest_name='IARU-HF')