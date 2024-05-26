from abc import ABC, abstractmethod
from typing import Dict, List, Set


class RealEstateScraper(ABC):
    @abstractmethod
    def process_postcode(self, postcode_number: str, seen_listings: Set[str]) -> Dict[str, Dict[str, str]]:
        pass

    @abstractmethod
    def process_page_listings(self, postcode_number: int, page_listings: List, listing_info: Dict[str, Dict[str, str]], seen_listings: Set[str]) -> bool:
        pass
