import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from helper import generate_postcodes
from typing import List
import time
import random

def get_soup(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    return BeautifulSoup(response.text, 'lxml')

def process_postcode(postcode_number: str) -> None:
    page_number = 1
    postcode_results = set()
    while True:
        print(f"Processing postcode {postcode_number}, page {page_number}")
        url = f"https://www.domain.com.au/rent/?postcode={postcode_number}&ssubs=0&sort=price-asc&page={page_number}"
        soup = get_soup(url)
        if soup is None:
            break
        error_page_found = soup.find(attrs={"data-testid": "error-page__message-header"})
        page_not_found = soup.find('div', class_='css-18vn4hf')
        if error_page_found or page_not_found:
            break
        parse_result = [a['href'] for a in soup.select('[data-testid^="listing-"] a')]
        postcode_results.update(parse_result)
        page_number += 1
        # random sleep to avoid being blocked
        time.sleep(random.uniform(0.2, 0.8))
    
    with open("output.csv", "a") as f:
        for url in postcode_results:
            listing_id = url.split("-")[-1]
            f.write(f"{postcode_number},{url},{listing_id}\n")
        

def main(postcodes: List[str]):
    with open("output.csv", "w") as f:
        f.write("postcode,url,listing_id\n")
    for postcode in postcodes:
        process_postcode(postcode)

postcodes = generate_postcodes()
main(postcodes)
