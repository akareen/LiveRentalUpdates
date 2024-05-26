from typing import Dict, List, Set
import datetime

from scrapers.abstract_scraper import RealEstateScraper
from utils import get_soup, convert_to_weekly_price


class DomainScraper(RealEstateScraper):
    IMPLEMENTED = True

    def process_postcode(self, postcode_number: str, seen_listings: Set[str]) -> Dict[str, Dict[str, str]]:
        """
        Process a given postcode to scrape real estate listings and return new listings.

        Args:
            postcode_number (str): The postcode number to process.
            seen_listings (Set[str]): A set of listing IDs that have already been seen.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary containing new listings found in the postcode.
        """
        page_number = 1
        listing_info: Dict[str, Dict[str, str]] = {}

        while True:
            print(f"Processing postcode {postcode_number}, page {page_number}")
            url = f"https://www.domain.com.au/rent/?excludedeposittaken=1&ssubs=0&sort=dateupdated-desc&postcode={postcode_number}&page={page_number}"
            soup = get_soup(url)
            if soup is None:
                break
            error_page_found = soup.find(attrs={"data-testid": "error-page__message-header"})
            page_not_found = soup.find('div', class_='css-18vn4hf')
            if error_page_found or page_not_found:
                break
            
            page_listings = soup.select('[data-testid^="listing-card-wrapper-"]')
            unique_seen = self.process_page_listings(postcode_number, page_listings, listing_info, seen_listings)
            if not unique_seen:
                break
            
            page_number += 1
        
        return listing_info

    def process_page_listings(
        self, 
        postcode_number: str, 
        page_listings: List, 
        listing_info: Dict[str, Dict[str, str]], 
        seen_listings: Set[str]
    ) -> bool:
        """
        Process the listings on a page and update the listing information.

        Args:
            postcode_number (str): The postcode number being processed.
            page_listings (List): A list of listings on the page.
            listing_info (Dict[str, Dict[str, str]]): A dictionary to store new listing information.
            seen_listings (Set[str]): A set of listing IDs that have already been seen.

        Returns:
            bool: True if new listings were found, False otherwise.
        """
        unique_seen = False
        for listing in page_listings:
            price_element = listing.select_one('[data-testid="listing-card-price"]')
            if price_element:
                price = price_element.get_text(strip=True)
                weekly_price = convert_to_weekly_price(price)
            else:
                weekly_price = None
            listing_link = listing.select_one('a.address.is-two-lines.css-1y2bib4')
            listing_url: str = listing_link['href']
            listing_id: str = listing_url.split("-")[-1]

            features_list: List[str] = [container.text.strip().split()[0] for container in listing.select('[data-testid="property-features-text-container"]')]

            if listing_id not in seen_listings:
                listing_info[f"domain-{listing_id}"] = {
                    'source': 'domain.com.au',
                    'postcode': str(postcode_number),
                    'listing_id': listing_id,
                    'url': listing_url, 
                    'beds': features_list[0] if features_list else None, 
                    'bath': features_list[1] if len(features_list) >= 2 else None, 
                    'weekly_price': str(weekly_price) if weekly_price else None,
                    'scrape_timestamp': datetime.datetime.timestamp(datetime.datetime.now()),
                    'html': str(listing)
                }
                unique_seen = True

        return unique_seen
