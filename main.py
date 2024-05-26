from typing import Dict, List, Set
import concurrent.futures
import sys
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

from utils import generate_postcodes
from scrapers.abstract_scraper import RealEstateScraper
from scrapers.domain_scraper import DomainScraper
from scrapers.rea_scraper import REAScraper

load_dotenv()

def get_mongo_client() -> MongoClient:
    """
    Get a MongoDB client using connection details from environment variables.

    Returns:
        MongoClient: A MongoDB client instance.

    Raises:
        ValueError: If any MongoDB connection details are missing in environment variables.
    """
    username = os.getenv("MONGO_USERNAME")
    password = os.getenv("MONGO_PASSWORD")
    host = os.getenv("MONGO_HOST")
    options = os.getenv("MONGO_OPTIONS")
    
    if not all([username, password, host, options]):
        raise ValueError("MongoDB connection details are not fully set in environment variables")
    
    connection_string = (
        f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@{host}/{options}"
    )
    return MongoClient(connection_string)

def read_seen_listings(db: MongoClient, collection_name: str) -> Set[str]:
    """
    Read the list of seen listings from the MongoDB collection.

    Args:
        db (MongoClient): The MongoDB client instance.
        collection_name (str): The name of the collection to read from.

    Returns:
        Set[str]: A set of listing IDs that have already been seen.
    """
    collection = db[collection_name]
    seen_listings = set()
    for listing in collection.find({}, {"_id": 0, "listing_id": 1}):
        seen_listings.add(listing["listing_id"])
    return seen_listings

def write_new_listings(db: MongoClient, collection_name: str, new_listings: Dict[str, Dict[str, str]]) -> None:
    """
    Write new listings to the MongoDB collection.

    Args:
        db (MongoClient): The MongoDB client instance.
        collection_name (str): The name of the collection to write to.
        new_listings (Dict[str, Dict[str, str]]): A dictionary containing new listings to be added.
    """
    collection = db[collection_name]
    operations = []

    for postcode, listings in new_listings.items():
        for listing_id, listing_info in listings.items():
            listing_info['_id'] = listing_id  # Use listing_id as _id
            operations.append(
                UpdateOne(
                    {"_id": listing_id},
                    {"$set": listing_info},
                    upsert=True
                )
            )

    if operations:
        collection.bulk_write(operations)

def main(db_name: str = 'realestate', collection_name: str = 'listings') -> None:
    """
    Main function to orchestrate the scraping and storing of real estate listings.

    Args:
        db_name (str, optional): The name of the MongoDB database. Defaults to 'realestate'.
        collection_name (str, optional): The name of the MongoDB collection. Defaults to 'listings'.
    """
    postcodes: List[str] = generate_postcodes()
    client = get_mongo_client()
    db = client[db_name]
    seen_listings: Set[str] = read_seen_listings(db, collection_name)
    print(f"Loaded {len(seen_listings)} seen listings")

    postcode_listing_info: Dict[str, Dict[str, str]] = dict()
    total_new_listings = 0
    scrapers: List[RealEstateScraper] = [DomainScraper(), REAScraper()]

    for scraper in scrapers:
        if not scraper.IMPLEMENTED:
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
    write_new_listings(db, collection_name, postcode_listing_info)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(db_name=sys.argv[1], collection_name=sys.argv[2])
    else:
        main()
