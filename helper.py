import requests
from bs4 import BeautifulSoup
import re
from typing import List, Union


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
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    return BeautifulSoup(response.text, 'html.parser')


def convert_to_weekly_price(price: str) -> Union[int, None]:
    price = price.lower().replace(",", "").strip()
    
    # Extract numeric value from the price string
    match = re.search(r"\d+(\.\d+)?", price)
    if not match:
        print(f"Error: Unable to extract numeric value from '{price}'")
        return None
    
    price_value = float(match.group())
    
    if "pw" in price or "per week" in price:
        return round(price_value)
    
    elif "pm" in price or "per month" in price:
        return round(price_value / 4.345)
    
    elif "py" in price or "per year" in price or "per annum" in price:
        return round(price_value / 52)
    
    elif "$" in price:
        return round(price_value)
    
    else:
        print(f"Error: Unable to determine price frequency from '{price}'")
        return None