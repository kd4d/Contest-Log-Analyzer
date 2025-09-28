import argparse
import os
import json
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# --- Constants ---
INDEX_FILENAME = "cty_index.json"
DATA_SUBDIR = "Data"
CTY_SUBDIR = "CTY"
USER_AGENT = "CTYFileIndexer/1.0 (Python)"

def build_full_index(base_url):
    """
    Scrapes the country-files website to build a complete index of all CTY files.

    Args:
        base_url (str): The main URL of the website containing the Archives widget.

    Returns:
        list: A list of dictionaries, where each dictionary represents a file.
              Returns an empty list if the initial page fetch fails.
    """
    print(f"Fetching base URL to find yearly archives: {base_url}")
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch the base URL. {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    archive_widget = soup.select_one('aside#baw_widgetarchives_widget_my_archives-2')
    
    if not archive_widget:
        print("Error: Could not find the Archives widget on the page.")
        return []

    year_links = [a['href'] for a in archive_widget.select('li.baw-year > a')]
    print(f"Found {len(year_links)} years to scan: {[link.split('/')[-2] for link in year_links]}")

    full_index = []
    for year_url in year_links:
        year = year_url.rstrip('/').split('/')[-1]
        print(f"\n--- Scanning Year: {year} ---")
        
        page_num = 1
        while True:
            page_url = f"{year_url}page/{page_num}/"
            print(f"  Fetching {page_url}...")
            
            try:
                page_response = requests.get(page_url, headers=headers)
                if page_response.status_code == 404:
                    print("  Reached the last page for this year.")
                    break 
                page_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"  Warning: Could not fetch {page_url}. {e}")
                break

            page_soup = BeautifulSoup(page_response.text, 'html.parser')
            articles = page_soup.find_all('article')

            if not articles:
                print("  No articles found on this page, ending year scan.")
                break

            for article in articles:
                # Find the primary CTY.DAT zip file link
                download_link = article.select_one('a[href*="/cty/download/"][href$=".zip"]')
                time_tag = article.find('time', class_='entry-date')

                if download_link and time_tag:
                    file_url = urljoin(base_url, download_link['href'])
                    zip_name = os.path.basename(file_url)
                    dat_filename = zip_name.replace('.zip', '.dat')
                    
                    file_entry = {
                        "date": time_tag['datetime'],
                        "url": file_url,
                        "zip_name": zip_name,
                        # local_path will be populated by the main function
                        "local_path": os.path.join(year, dat_filename) 
                    }
                    full_index.append(file_entry)
                    print(f"    + Found: {zip_name} ({time_tag['datetime']})")

            page_num += 1

    # Sort the final index by date, newest first, for easy processing later
    full_index.sort(key=lambda x: x['date'], reverse=True)
    return full_index

def main():
    """ Main function to parse arguments and save the index. """
    parser = argparse.ArgumentParser(
        description="Build a JSON index of all cty.dat files from country-files.com."
    )
    parser.add_argument(
        "url",
        help="The base URL of the website (e.g., 'https://www.country-files.com/')."
    )
    args = parser.parse_args()

    contest_input_dir = os.getenv("CONTEST_INPUT_DIR")
    if not contest_input_dir:
        raise EnvironmentError("Error: CONTEST_INPUT_DIR environment variable is not set.")

    # Define the output directory and create it if it doesn't exist
    cty_data_path = os.path.join(contest_input_dir, DATA_SUBDIR, CTY_SUBDIR)
    os.makedirs(cty_data_path, exist_ok=True)

    # Build the full index by scraping the website
    cty_index = build_full_index(args.url)

    if not cty_index:
        print("\nNo index data was generated. Exiting.")
        return

    # Finalize the local_path to be absolute for portability
    for entry in cty_index:
        entry['local_path'] = os.path.join(cty_data_path, entry['local_path'])

    # Save the index to the JSON file
    output_filepath = os.path.join(cty_data_path, INDEX_FILENAME)
    print(f"\nFound a total of {len(cty_index)} files.")
    
    try:
        with open(output_filepath, 'w') as f:
            json.dump(cty_index, f, indent=2)
        print(f"Successfully created index file at: {output_filepath}")
    except IOError as e:
        print(f"Error: Could not write index file. {e}")

if __name__ == "__main__":
    main()