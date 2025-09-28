import argparse
import os
import json
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import zipfile
import io

# ---
# Technical Debt
#
# This script now incorporates a more complex data management flow:
#
# 1. Index Auto-Creation (Step 2): If the index file (cty_index.json) is
#    not found, the script automatically triggers a full, one-time scan of
#    the website to build it from scratch. This makes the script fully
#    self-initializing.
#
# 2. Incremental Updates (Step 3): An update check is triggered under
#    specific conditions. If a user requests a file 'before' a date, and
#    that date is newer than any file in our index, the script will
#    attempt to find newer files online.
# ---

# --- Constants ---
INDEX_FILENAME = "cty_index.json"
DATA_SUBDIR = "Data"
CTY_SUBDIR = "CTY"
BASE_URL = "https://www.country-files.com/"
USER_AGENT = "CTYFileFinder/2.1 (Python)"


def _build_full_index(cty_data_path: str) -> list:
    """
    Performs a one-time, full scrape of the website to build the index.
    """
    print("Index not found. Performing initial full build, this may take a moment...")
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(BASE_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        archive_widget = soup.select_one('aside#baw_widgetarchives_widget_my_archives-2')
        if not archive_widget:
            print("Error: Could not find the Archives widget for initial build.")
            return []
        year_links = [a['href'] for a in archive_widget.select('li.baw-year > a')]
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch base URL for initial build. {e}")
        return []

    full_index = []
    for year_url in year_links:
        year = year_url.rstrip('/').split('/')[-1]
        print(f"--- Scanning Year: {year} ---")
        page_num = 1
        while True:
            page_url = f"{year_url}page/{page_num}/"
            try:
                page_response = requests.get(page_url, headers=headers, timeout=10)
                if page_response.status_code == 404: break
                page_response.raise_for_status()
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                articles = page_soup.find_all('article')
                if not articles: break
                for article in articles:
                    link = article.select_one('a[href*="/cty/download/"][href$=".zip"]')
                    time_tag = article.find('time', class_='entry-date')
                    if link and time_tag:
                        zip_name = os.path.basename(link['href'])
                        dat_filename = zip_name.replace('.zip', '.dat')
                        full_index.append({
                            "date": time_tag['datetime'],
                            "url": urljoin(BASE_URL, link['href']),
                            "zip_name": zip_name,
                            "local_path": os.path.join(cty_data_path, year, dat_filename)
                        })
                page_num += 1
            except requests.exceptions.RequestException:
                break 

    full_index.sort(key=lambda x: x['date'], reverse=True)
    return full_index


def _update_index_incrementally(cty_index: list, cty_data_path: str) -> list:
    """
    Scrapes for files newer than the latest entry in the provided index.
    """
    latest_date_in_index = cty_index[0]['date']
    print(f"Checking for files newer than {latest_date_in_index}...")
    
    start_year = int(datetime.fromisoformat(latest_date_in_index).year)
    current_year = datetime.now().year
    
    new_files = []
    headers = {'User-Agent': USER_AGENT}

    for year in range(start_year, current_year + 1):
        print(f"--- Checking for updates in {year} ---")
        page_num = 1
        while True:
            page_url = f"{BASE_URL}{year}/page/{page_num}/"
            should_stop = False
            try:
                res = requests.get(page_url, headers=headers, timeout=10)
                if res.status_code == 404: break
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                articles = soup.find_all('article')
                if not articles: break
                
                for article in articles:
                    time_tag = article.find('time', class_='entry-date')
                    if time_tag and time_tag['datetime'] > latest_date_in_index:
                        link = article.select_one('a[href*="/cty/download/"][href$=".zip"]')
                        if link:
                            zip_name = os.path.basename(link['href'])
                            dat_filename = zip_name.replace('.zip', '.dat')
                            new_files.append({
                                "date": time_tag['datetime'],
                                "url": urljoin(BASE_URL, link['href']),
                                "zip_name": zip_name,
                                "local_path": os.path.join(cty_data_path, str(year), dat_filename)
                            })
                    elif time_tag and time_tag['datetime'] <= latest_date_in_index:
                        should_stop = True
                        break
                if should_stop: break
                page_num += 1
            except requests.exceptions.RequestException:
                break
    
    if new_files:
        print(f"Found {len(new_files)} new files.")
        # Prepend new files and re-sort to be safe
        updated_index = new_files + cty_index
        updated_index.sort(key=lambda x: x['date'], reverse=True)
        return updated_index
    else:
        print("No new files found. Index is up to date.")
        return cty_index

def _download_and_cache_file(file_entry: dict) -> str | None:
    local_dat_path = file_entry['local_path']
    if os.path.exists(local_dat_path):
        print(f"File is already cached: {local_dat_path}")
        return local_dat_path

    print(f"File not in cache. Downloading '{file_entry['zip_name']}'...")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(file_entry['url'], headers=headers)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            dat_content = thezip.read('cty.dat')
        os.makedirs(os.path.dirname(local_dat_path), exist_ok=True)
        with open(local_dat_path, 'wb') as f:
            f.write(dat_content)
        print(f"Successfully downloaded and saved: {local_dat_path}")
        return local_dat_path
    except (requests.exceptions.RequestException, zipfile.BadZipFile, KeyError, IOError) as e:
        print(f"Error: Failed to download, extract, or save file. {e}")
        return None

def find_cty_file_by_date(target_date: datetime, mode: str, cty_data_path: str) -> str | None:
    index_path = os.path.join(cty_data_path, INDEX_FILENAME)
    
    try:
        with open(index_path, 'r') as f:
            cty_index = json.load(f)
    except FileNotFoundError:
        cty_index = _build_full_index(cty_data_path)
        if cty_index:
            with open(index_path, 'w') as f:
                json.dump(cty_index, f, indent=2)
            print(f"Initial index build complete. Saved to {index_path}")
        else:
            print("Failed to build initial index. Cannot proceed.")
            return None

    target_entry = None
    target_date_str = target_date.isoformat()
    
    if mode == 'before':
        candidates = [e for e in cty_index if e['date'] <= target_date_str]
        if not candidates:
            print(f"No file found on or before {target_date.date()}.")
            return None
        target_entry = candidates[0]

        # --- NEW LOGIC ---
        # Check if the target date is beyond our latest known file.
        is_any_file_newer = any(e['date'] > target_date_str for e in cty_index)
        if not is_any_file_newer:
            print("\nWarning: Target date is newer than latest file in index. Checking for updates.")
            original_count = len(cty_index)
            cty_index = _update_index_incrementally(cty_index, cty_data_path)
            
            if len(cty_index) > original_count:
                with open(index_path, 'w') as f: json.dump(cty_index, f, indent=2)
                print("Index was updated. Re-evaluating best match...")
                # Re-run selection as the best match may have changed
                candidates = [e for e in cty_index if e['date'] <= target_date_str]
                target_entry = candidates[0]

            # After the update attempt, check one last time.
            if not any(e['date'] > target_date_str for e in cty_index):
                print("Warning: The selected CTY file may be out of date. No newer files were found online.")
        # --- END NEW LOGIC ---

    elif mode == 'after':
        candidates = [e for e in cty_index if e['date'] >= target_date_str]
        if not candidates:
            # If no file is found, the index might be out of date. Trigger update.
            print(f"No file found on or after {target_date.date()}. Checking for updates.")
            original_count = len(cty_index)
            cty_index = _update_index_incrementally(cty_index, cty_data_path)
            if len(cty_index) > original_count:
                with open(index_path, 'w') as f: json.dump(cty_index, f, indent=2)
                print("Index was updated. Re-evaluating best match...")
                candidates = [e for e in cty_index if e['date'] >= target_date_str]

        if candidates:
            target_entry = candidates[-1]

    if not target_entry:
        print(f"No suitable file found for the date '{target_date.date()}' with mode '{mode}'.")
        return None

    print(f"\nFound best match: {target_entry['zip_name']} (Date: {target_entry['date']})")
    return _download_and_cache_file(target_entry)


def main():
    parser = argparse.ArgumentParser(description="Finds and retrieves a cty.dat file by date.")
    parser.add_argument("date", help="The target date in YYYY-MM-DD format.")
    parser.add_argument("mode", choices=['before', 'after'], type=str.lower, help="Mode: 'before' or 'after'.")
    args = parser.parse_args()

    try:
        # We care about the whole day, so set time to the very end of the day for 'before' logic.
        target_date = datetime.fromisoformat(args.date + "T23:59:59")
    except ValueError:
        print("Error: Date format is invalid. Please use YYYY-MM-DD.")
        return

    contest_input_dir = os.getenv("CONTEST_INPUT_DIR")
    if not contest_input_dir:
        raise EnvironmentError("Error: CONTEST_INPUT_DIR environment variable is not set.")

    cty_data_path = os.path.join(contest_input_dir, DATA_SUBDIR, CTY_SUBDIR)
    
    final_path = find_cty_file_by_date(target_date, args.mode, cty_data_path)

    if final_path:
        print("\nOperation complete.")
        print(f"Final file path: {final_path}")
    else:
        print("\nOperation failed.")

if __name__ == "__main__":
    main()