from helper import generate_postcodes, get_soup, convert_to_weekly_price
from typing import Dict, List, Set
import csv
import concurrent.futures
import pandas as pd

def read_csv_into_set(file_path: str) -> Set[str]:
    df = pd.read_csv(file_path, header=0)
    listing_id_set = set(df['listing_id'].astype(str))
    return listing_id_set

def process_postcode(postcode_number: str, seen_listings: Set[str]) -> Dict[str, Dict[str, str]]:
    page_number = 1
    listing_info: Dict[str, Dict[str, str]] = dict()

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
        unique_seen =  process_page_listings(postcode_number, page_listings, listing_info, seen_listings)
        if not unique_seen:
            break
        
        page_number += 1
    
    return listing_info


def process_page_listings(postcode_number: int, page_listings: List, listing_info: Dict[str, Dict[str, str]], seen_listings: Set[str]) -> bool:
    unique_seen = False
    for listing in page_listings:
        price_element = listing.select_one('[data-testid="listing-card-price"]')
        if price_element:
            price = price_element.get_text(strip=True)
            weekly_price = convert_to_weekly_price(price)
        else:
            weekly_price = None
        listing_link = listing.select_one('a.address.is-two-lines.css-1y2bib4')
        listing_url = listing_link['href']
        listing_id = listing_url.split("-")[-1]

        features_list = [container.text.strip().split()[0] for container in listing.select('[data-testid="property-features-text-container"]')]

        if listing_id not in seen_listings:
            listing_info[listing_id] = {
                'postcode': postcode_number,
                'listing_id': listing_id,
                'url': listing_url, 
                'beds': features_list[0] if features_list else None, 
                'bath': features_list[1] if features_list else None, 
                'weekly_price': weekly_price, 
                'html': str(listing)
            }
            unique_seen = True

    return unique_seen


def _write_listings_to_csv(original_file_path: str, new_listing_info: Dict[str, Dict[str, str]]) -> None:
    df = pd.read_csv(original_file_path, header=0)
    
    data_to_append = []
    for postcode, info in new_listing_info.items():
        for listing_id, listing_info in info.items():
            listing_info.pop('html')
            data_to_append.append(listing_info)
    
    new_df = pd.DataFrame(data_to_append)
    updated_df = pd.concat([df, new_df], ignore_index=True)
    updated_df.sort_values(by='postcode', inplace=True)

    updated_df.to_csv(original_file_path, index=False)


def main(postcodes: List[str], csv_file_path: str):
    seen_listings: Set[str] = read_csv_into_set(csv_file_path)
    print(f"Loaded {len(seen_listings)} seen listings")

    postcode_listing_info: Dict[str, Dict[str, str]] = dict()
    total_new_listings = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_postcode = {executor.submit(process_postcode, postcode, seen_listings): postcode for postcode in postcodes}

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
    _write_listings_to_csv(
        original_file_path=csv_file_path,
        new_listing_info=postcode_listing_info
    )


if __name__ == "__main__":
    postcodes = generate_postcodes()
    main(
        postcodes=postcodes,
        csv_file_path='output.csv'
    )
