import os
import mechanicalsoup as ms
import redis
from pymongo import MongoClient
from urllib.parse import urlparse, urlunparse
import time

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

# avoids duplicate links that differ only in query parameters
def normalize_url(url):
    parsed_url = urlparse(url)
    # Remove query parameters for normalization
    return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

def crawl(browser, r, mongo, url, graveyard, parent_map):
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
                parent_map[normalized_link] = normalized_current_url  # Track the parent-child relationship

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

def reconstruct_path(parent_map, start_url, target_url):
    path = []
    current_url = target_url
    while current_url != start_url:
        path.append(current_url)
        current_url = parent_map.get(current_url)
        if current_url is None:
            print("Error: Path not found.")
            return []
    path.append(start_url)
    path.reverse()
    return path

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

# Initialize the graveyard set to keep track of visited URLs
graveyard = set()

# Initialize the parent map to track the path
parent_map = {}

# Start crawl
crawled_count = 0
found = False
while link := r.rpop("links"):
    if not crawl(browser, r, mongo, link, graveyard, parent_map):
        found = True
        break
    crawled_count += 1

# Close connection to MongoDB
mongo.close()

print(f"Crawl completed. Total pages crawled: {crawled_count}")

# Reconstruct the path if the target was found
if found:
    path = reconstruct_path(parent_map, start_url, TARGET_URL)
    print("Path from Batman: Arkham Knight to God of War:")
    for p in path:
        print(p)
else:
    print("God of War page not found.")