# test_code/prototype_arrl_scraper.py
import argparse
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from typing import List, Dict


class ARRLScraperPrototype:
    """
    Prototype scraper for ARRL contests which share a similar website structure.
    """
    base_url = "https://contests.arrl.org/"
    CONTEST_EIDS: Dict[str, int] = {
        "ARRL-SS-CW": 17,
        "ARRL-SS-PH": 18,
        "ARRL-DX-CW": 13,
        "ARRL-DX-SSB": 14,
        "ARRL-10": 21,
        "IARU-HF": 4
    }

    @classmethod
    def get_supported_contests(cls) -> List[str]:
        """Returns a list of all supported contest names."""
        return sorted(list(cls.CONTEST_EIDS.keys()))

    def scrape_and_save(self, year: int, contest: str, callsign: str, save_path: Path) -> bool:
        """
        Scrapes the ARRL website for a single log and saves it to the specified path.
        This is a two-hop process: first find the year link, then the callsign link.
        """
        logging.info(f"Attempting to download log for {callsign} from {contest}...")

        eid = self.CONTEST_EIDS.get(contest.upper())
        if not eid:
            logging.error(f"Invalid contest specified: '{contest}'.")
            return False

        initial_url = f"{self.base_url}publiclogs.php?eid={eid}"
        headers = {'User-Agent': 'Contest-Log-Analyzer/Downloader/1.0'}

        try:
            # --- Hop 1: Get the year-specific link ---
            logging.info(f"Fetching main contest page: {initial_url}")
            response1 = requests.get(initial_url, headers=headers, timeout=15)
            response1.raise_for_status()

            soup1 = BeautifulSoup(response1.text, 'html.parser')
            year_link_tag = soup1.find('a', string=str(year))

            if not year_link_tag or not year_link_tag.has_attr('href'):
                logging.error(f"Could not find a link for the year {year} on the main contest page.")
                return False

            year_page_url = urljoin(self.base_url, year_link_tag['href'])

            # --- Hop 2: Get the callsign-specific link ---
            logging.info(f"Fetching year index page: {year_page_url}")
            response2 = requests.get(year_page_url, headers=headers, timeout=15)
            response2.raise_for_status()

            soup2 = BeautifulSoup(response2.text, 'html.parser')
            callsign_link_tag = soup2.find('a', string=lambda text: text and text.upper() == callsign.upper())

            if not callsign_link_tag or not callsign_link_tag.has_attr('href'):
                logging.warning(f"Log for callsign '{callsign}' not found on the {year} index page.")
                return False

            log_page_url = urljoin(self.base_url, callsign_link_tag['href'])

            # --- Final Download ---
            logging.info(f"Downloading log from: {log_page_url}")
            log_response = requests.get(log_page_url, headers=headers, timeout=15)
            log_response.raise_for_status()
            log_content = log_response.text

            # --- Save the File ---
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(log_content)

            logging.info(f"Successfully saved log to {save_path}")
            return True

        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error for {callsign}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logging.error(f"A network error occurred for {callsign}: {e}")
            return False
        except Exception as e:
            logging.error(f"An unexpected error occurred for {callsign}: {e}")
            return False

def main():
    """Main driver for the standalone prototype script."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    supported_contests = ARRLScraperPrototype.get_supported_contests()

    parser = argparse.ArgumentParser(description="Prototype scraper for ARRL public logs.")
    parser.add_argument('--year', required=True, type=int, help="Contest year (e.g., 2024)")
    parser.add_argument('--contest', required=True, choices=supported_contests, help="Contest name")
    parser.add_argument('--call', required=True, help="A single callsign to download")
    args = parser.parse_args()

    output_filename = Path(f"./{args.call.upper()}.log")

    scraper = ARRLScraperPrototype()

    print("-" * 40)
    success = scraper.scrape_and_save(
        year=args.year,
        contest=args.contest,
        callsign=args.call,
        save_path=output_filename
    )
    print("-" * 40)

    if success:
        print(f"Result for {args.call}: Success. Log saved to '{output_filename}'.")
    else:
        print(f"Result for {args.call}: Failed. See logs for details.")

    print("\nSupported Contests:")
    for contest in supported_contests:
        print(f"- {contest}")

if __name__ == '__main__':
    main()