import os
import mechanicalsoup as ms
import redis
from pymongo import MongoClient

MAX_PAGES = 100  # Set the maximum number of pages to crawl
TARGET_URL = "https://store.steampowered.com/app/1593500/God_of_War/"  # End goal URL

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

def crawl(browser, r, mongo, url, crawled_count):
    if crawled_count >= MAX_PAGES:
        return False  # Stop crawling
    print("Downloading url:", url)
    browser.open(url)

    # Check if we have reached the target URL
    if url.decode('utf-8') == TARGET_URL:
        print("Found the target page!")
        return False

    # Parse the page content for links
    print("Parsing for more links")
    a_tags = browser.page.find_all("a")
    hrefs = [a.get("href") for a in a_tags if a.get("href")]

    steam_store_domain = "https://store.steampowered.com"
    links = []
    for href in hrefs:
        if href.startswith("/app/") or href.startswith("https://store.steampowered.com/app/"):
            full_link = steam_store_domain + href if href.startswith("/app/") else href
            if full_link != url.decode('utf-8'):
                links.append(full_link)

    # Remove duplicates
    links = list(set(links))

    print("Valid links found:", links)

    # Push valid links onto Redis
    if links:
        r.lpush("links", *links)
        mongo.add_links(url, links)
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

# Start crawl
crawled_count = 0
while link := r.rpop("links"):
    if not crawl(browser, r, mongo, link, crawled_count):
        break
    crawled_count += 1

# Close connection to MongoDB
mongo.close()
