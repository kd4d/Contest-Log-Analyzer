# test_code/prototype_cq_scraper.py
import argparse
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, List, Dict


class CQScraperPrototype:
    """
    Prototype scraper for CQ contests (WPX, WW, 160) which share a similar website structure.
    """
    CONTEST_URLS: Dict[str, str] = {
        "WPX": "https://cqwpx.com/",
        "WW": "https://cqww.com/",
        "160": "https://cq160.com/",
    }

    @classmethod
    def get_supported_contests(cls) -> List[str]:
        """Returns a list of all supported contest names."""
        contests = []
        for family in cls.CONTEST_URLS.keys():
            contests.append(f"CQ-{family}-CW")
            contests.append(f"CQ-{family}-SSB")
        return sorted(contests)

    def scrape_and_save(self, year: int, contest: str, callsign: str, save_path: Path, event: Optional[str] = None) -> bool:
        """
        Scrapes the appropriate CQ contest website for a single log and saves it.
        Returns True on success, False on failure.
        """
        logging.info(f"Attempting to download log for {callsign} from {contest}...")

        # 1. Determine contest family and base URL
        try:
            contest_family = contest.split('-')[1].upper()
            base_url = self.CONTEST_URLS.get(contest_family)
            if not base_url:
                logging.error(f"Unsupported contest family for CQ scraper: '{contest_family}'")
                return False
        except IndexError:
            logging.error(f"Could not determine contest family from name: '{contest}'")
            return False

        # 2. Construct the URL for the year/mode index page.
        try:
            mode = contest.split('-')[-1].lower()
            if mode not in ['cw', 'ssb']:
                logging.error(f"Invalid contest mode '{mode}' derived from '{contest}'. Must be 'CW' or 'SSB'.")
                return False
        except IndexError:
            logging.error(f"Could not determine mode from contest name: '{contest}'")
            return False

        # Use 'ph' for SSB as observed in the site structure
        mode_suffix = 'ph' if mode == 'ssb' else 'cw'
        index_url = f"{base_url}publiclogs/{year}{mode_suffix}/"

        try:
            # 3. Fetch the HTML of the index page.
            logging.info(f"Fetching index page: {index_url}")
            headers = {'User-Agent': 'Contest-Log-Analyzer/Downloader/1.0'}
            response = requests.get(index_url, headers=headers, timeout=15)
            response.raise_for_status()

            # 4. Parse the HTML to find the link for the target callsign.
            soup = BeautifulSoup(response.text, 'html.parser')
            log_link_tag = soup.find('a', string=lambda text: text and text.upper() == callsign.upper())

            if not log_link_tag or not log_link_tag.has_attr('href'):
                logging.warning(f"Log for callsign '{callsign}' not found on the index page.")
                return False

            # 5. Construct the final log URL.
            log_filename = log_link_tag['href']
            final_log_url = f"{index_url}{log_filename}"

            # 6. Download the raw text content of the log.
            logging.info(f"Downloading log from: {final_log_url}")
            log_response = requests.get(final_log_url, headers=headers, timeout=15)
            log_response.raise_for_status()
            log_content = log_response.text

            # 7. Save the content to the provided save_path.
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

    supported_contests = CQScraperPrototype.get_supported_contests()

    parser = argparse.ArgumentParser(description="Prototype scraper for CQ public logs.")
    parser.add_argument('--year', required=True, type=int, help="Contest year (e.g., 2023)")
    parser.add_argument('--contest', required=True, choices=supported_contests, help="Contest name")
    parser.add_argument('--call', required=True, help="A single callsign to download")
    args = parser.parse_args()

    # Save the file to the local directory where the script is run
    output_filename = Path(f"./{args.call.upper()}.log")

    scraper = CQScraperPrototype()

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