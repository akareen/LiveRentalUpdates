from typing import Dict, List, Set
from scrapers.abstract_scraper import RealEstateScraper


class REAScraper(RealEstateScraper):
    IMPLEMENTED = False

    def process_postcode(self, postcode_number: str, seen_listings: Set[str]) -> Dict[str, Dict[str, str]]:
        page_number = 1
        listing_info: Dict[str, Dict[str, str]] = dict()

        # TODO: Implement this method

        return listing_info
    
    def process_page_listings(self, postcode_number: int, page_listings: List, listing_info: Dict[str, Dict[str, str]], seen_listings: Set[str]) -> bool:
        # TODO: Implement this method
        return False
