# test_code/prototype_wae_scraper.py
import argparse
import logging
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlencode

class WAEScraperPrototype:
    """
    Prototype scraper for the WAE contests hosted on the DARC server.
    """
    base_url = "https://dxhf2.darc.de/"
    CONTEST_DATA: Dict[str, Dict[str, str]] = {
        "WAE-SSB": {"path": "~waessblog/", "param": "waessb"},
        "WAE-CW": {"path": "~waecwlog/", "param": "waecw"},
        "WAE-RTTY": {"path": "~waerttylog/", "param": "waertty"},
    }

    @classmethod
    def get_supported_contests(cls) -> List[str]:
        """Returns a list of all supported contest names."""
        return sorted(list(cls.CONTEST_DATA.keys()))

    def scrape_and_save(self, year: int, contest: str, callsign: str, save_path: Path, event: Optional[str] = None) -> bool:
        """
        Scrapes the DARC WAE website for a single log and saves it.
        Returns True on success, False on failure.
        """
        logging.info(f"Attempting to download log for {callsign} from {contest}...")

        # 1. Look up contest-specific data
        contest_info = self.CONTEST_DATA.get(contest.upper())
        if not contest_info:
            logging.error(f"Unsupported contest for WAE scraper: '{contest}'")
            return False

        # 2. Construct the final URL with parameters
        params = {
            'call': callsign,
            'jahr': year,
            'fc': 'req_olog',
            'contest': contest_info['param'],
            'form': 'referat',
            'lang': 'en',
            'status': 'show'
        }
        
        full_url = f"{self.base_url}{contest_info['path']}user.cgi?{urlencode(params)}"

        try:
            # 3. Fetch the HTML of the log page.
            logging.info(f"Fetching log page: {full_url}")
            headers = {'User-Agent': 'Contest-Log-Analyzer/Downloader/1.0'}
            response = requests.get(full_url, headers=headers, timeout=15)
            response.raise_for_status()

            # 4. Parse the HTML to find the <pre> tag.
            soup = BeautifulSoup(response.text, 'html.parser')
            log_pre_tag = soup.find('pre')

            if not log_pre_tag:
                logging.warning(f"Log for callsign '{callsign}' not found. The page was retrieved, but it did not contain a <pre> log block.")
                return False

            log_content = log_pre_tag.get_text()

            # 5. Save the content to the provided save_path.
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
    
    supported_contests = WAEScraperPrototype.get_supported_contests()

    parser = argparse.ArgumentParser(description="Prototype scraper for DARC WAE public logs.")
    parser.add_argument('--year', required=True, type=int, help="Contest year (e.g., 2020)")
    parser.add_argument('--contest', required=True, choices=supported_contests, help="Contest name")
    parser.add_argument('--call', required=True, help="A single callsign to download")
    args = parser.parse_args()

    output_filename = Path(f"./{args.call.upper()}.log")

    scraper = WAEScraperPrototype()

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