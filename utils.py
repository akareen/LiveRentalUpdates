import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from typing import Dict, List, Set, Union


def generate_postcodes() -> List[str]:
    postcode_ranges = {
        'NSW': [(2000, 2599), (2619, 2899), (2921, 2999)],
        'ACT': [(2600, 2618), (2900, 2920)],
        'VIC': [(3000, 3999)],
        'QLD': [(4000, 4999)],
        'SA': [(5000, 5799)],
        'WA': [(6000, 6797)],
        'TAS': [(7000, 7799)],
        'NT': [(800, 899)]
    }

    valid_postcodes = []

    for state, ranges in postcode_ranges.items():
        for start, end in ranges:
            valid_postcodes.extend([str(code).zfill(4) for code in range(start, end + 1)])

    return valid_postcodes



def get_soup(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        params = {
            "noimg": 1  # Custom parameter to indicate no images
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    return BeautifulSoup(response.text, 'html.parser')


def convert_to_weekly_price(price: str) -> Union[int, None]:
    price = price.lower().replace(",", "").strip()
    
    match = re.search(r"\d+(\.\d+)?", price)
    if not match:
        print(f"Error: Unable to extract numeric value from '{price}'")
        return None
    
    price_value = float(match.group())
    
    if "pw" in price or "p/w" in price or "per week" in price or "/week" in price:
        return round(price_value)
    
    elif "pm" in price or "p/m" in price or "per month" in price:
        return round(price_value / 4.345)
    
    elif "py" in price or "p/y" in price or "per year" in price or "per annum" in price:
        return round(price_value / 52)
    
    elif "$" in price or price.isdigit():
        return round(price_value)
    
    else:
        print(f"Warning: Unable to determine price frequency from '{price}'")
        return None
    

def read_csv_into_set(file_path: str) -> Set[str]:
    try:
        df = pd.read_csv(file_path, header=0)
        listing_id_set = set(df['listing_id'].astype(str))
        return listing_id_set
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return set()


def write_listings_to_csv(original_file_path: str, new_listing_info: Dict[str, Dict[str, str]]) -> None:
    try:
        df = pd.read_csv(original_file_path, header=0)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        headers = ['source', 'postcode', 'listing_id', 'url', 'beds', 'bath', 'weekly_price', 'scrape_timestamp']
        df = pd.DataFrame(columns=headers)

    df = df.astype(str)

    data_to_append = []

    for postcode, info in new_listing_info.items():
        for listing_id, listing_info in info.items():
            listing_info.pop('html', None)
            data_to_append.append(listing_info)

    new_df = pd.DataFrame(data_to_append)

    updated_df = pd.concat([df, new_df], ignore_index=True)
    updated_df.sort_values(by='postcode', inplace=True)
    updated_df.to_csv(original_file_path, index=False)