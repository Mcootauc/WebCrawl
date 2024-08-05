import os
import mechanicalsoup as ms
import redis
from pymongo import MongoClient
from urllib.parse import urlparse, urlunparse
import time

MAX_PAGES = 500  # Increase the maximum number of pages to crawl
TARGET_URL = "https://store.steampowered.com/app/1593500/God_of_War/"  # End goal URL
STEAM_STORE_DOMAIN = "https://store.steampowered.com"
RETRY_LIMIT = 3  # Number of times to retry loading a page if it fails

class MongoDBConnector:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def close(self):
        self.client.close()

    def add_links(self, page, links):
        page = page.decode('utf-8')
        self.db.pages.insert_one({'url': page, 'links': links})
        print(f"Added page: {page} with links: {links}")

    def flush_db(self):
        print("Clearing MongoDB")
        self.db.pages.delete_many({})

def write_to_mongo(db, url, html):
    # Skipping storing the HTML for faster performance
    pass

def normalize_url(url):
    parsed_url = urlparse(url)
    # Remove query parameters for normalization
    return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

def crawl(browser, r, mongo, url, crawled_count, graveyard):
    if crawled_count >= MAX_PAGES:
        return False  # Stop crawling
    url = url.decode('utf-8')
    print("Downloading url:", url)

    # Retry logic
    retries = 0
    while retries < RETRY_LIMIT:
        try:
            browser.open(url)
            if browser.page is not None:
                break
        except Exception as e:
            print(f"Error loading {url}: {e}")
        retries += 1
        time.sleep(1)  # Wait a bit before retrying

    if browser.page is None:
        print(f"Failed to load {url} after {RETRY_LIMIT} retries")
        return True

    # Check if we have reached the target URL
    if url == TARGET_URL:
        print("Found the target page!")
        return False

    # Normalize current URL to avoid looping back to it
    normalized_current_url = normalize_url(url)
    graveyard.add(normalized_current_url)  # Add current URL to graveyard

    # Parse the page content for links
    print("Parsing for more links")
    a_tags = browser.page.find_all("a")
    hrefs = [a.get("href") for a in a_tags if a.get("href")]

    links = []
    for href in hrefs:
        if href.startswith("/") or href.startswith(STEAM_STORE_DOMAIN):
            full_link = STEAM_STORE_DOMAIN + href if href.startswith("/") else href
            normalized_link = normalize_url(full_link)
            if normalized_link not in graveyard:
                links.append(normalized_link)

    # Remove duplicates
    links = list(set(links))

    print("Valid links found:", links)

    # Push valid links onto Redis and add them to the graveyard
    if links:
        r.lpush("links", *links)
        mongo.add_links(url.encode('utf-8'), links)
        for link in links:
            graveyard.add(link)
    else:
        print("No valid links found on this page.")

    return True

### MAIN ###

# Initialize MongoDB (Replace with your MongoDB Atlas connection string)
mongo = MongoDBConnector("mongodb+srv://mcootauc:8fG1xnTUWWnkMoZ8@cluster1.dztsxzq.mongodb.net/web_crawler?retryWrites=true&w=majority&appName=Cluster1", "web_crawler")

# Clear the database before starting the crawl
mongo.flush_db()

# Initialize Redis
r = redis.Redis()
r.flushall()

# Initialize MechanicalSoup headless browser
browser = ms.StatefulBrowser()

# Add root URL as the entry point to our crawl
start_url = "https://store.steampowered.com/app/208650/Batman_Arkham_Knight/"
r.lpush("links", start_url)

# Add the Steam home page to the Redis queue to start the crawl from home as well
r.lpush("links", STEAM_STORE_DOMAIN)

# Initialize the graveyard set to keep track of visited URLs
graveyard = set()

# Start crawl
crawled_count = 0
while link := r.rpop("links"):
    if not crawl(browser, r, mongo, link, crawled_count, graveyard):
        break
    crawled_count += 1

# Close connection to MongoDB
mongo.close()
