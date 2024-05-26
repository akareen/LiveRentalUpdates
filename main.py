from typing import Dict, List, Set
import concurrent.futures
import sys

from utils import generate_postcodes, read_csv_into_set, write_listings_to_csv

from scrapers.abstract_scraper import RealEstateScraper
from scrapers.domain_scraper import DomainScraper
from scrapers.rea_scraper import REAScraper


def main(csv_file_path: str = 'output.csv') -> None:
    postcodes: List[str] = generate_postcodes()
    seen_listings: Set[str] = read_csv_into_set(csv_file_path)
    print(f"Loaded {len(seen_listings)} seen listings")

    postcode_listing_info: Dict[str, Dict[str, str]] = dict()
    total_new_listings = 0
    scrapers: List[RealEstateScraper] = [DomainScraper(), REAScraper()]

    for scraper in scrapers:
        if scraper.IMPLEMENTED == False:
            continue
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_postcode = {
                executor.submit(scraper.process_postcode, postcode, seen_listings): postcode 
                for postcode in postcodes
            }

            for future in concurrent.futures.as_completed(future_to_postcode):
                postcode = future_to_postcode[future]
                try:
                    listing_info = future.result()
                    postcode_listing_info[postcode] = listing_info

                    total_new_listings += len(listing_info)
                    print(f"Finished processing postcode {postcode}")
                    print(f"Found {len(listing_info)} new listings")
                except Exception as e:
                    print(f"Error processing postcode {postcode}: {e}")

    print(f"total_new_listings={total_new_listings}")
    write_listings_to_csv(
        original_file_path=csv_file_path,
        new_listing_info=postcode_listing_info
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(csv_file_path=sys.argv[1])
    else:
        main()
