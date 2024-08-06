<img width="1440" alt="Screenshot 2024-08-05 at 7 14 57 PM" src="https://github.com/user-attachments/assets/696a2309-d2aa-490e-9e06-df8f279ba2d9">
<img width="1440" alt="Screenshot 2024-08-05 at 7 12 56 PM" src="https://github.com/user-attachments/assets/bc7c6e28-c554-4ef1-b82d-0919f68da7e8">

# Steam Game Path Analysis Crawler

## Overview

This project is a web crawler designed to trace the path from the "Batman: Arkham Knight" game page to the "God of War" game page on Steam by following related game links. The crawler uses MechanicalSoup to navigate the Steam store, Redis to manage the queue of URLs to be crawled, and MongoDB to store the crawled links. It also tracks the path taken to reach the "God of War" page.

## Pipeline

### Components Used

1. **MechanicalSoup**: A library for automating interaction with websites.
2. **Redis**: An in-memory data structure store used as a queue to manage URLs to be crawled.
3. **MongoDB**: A NoSQL database used to store the crawled URLs and links.
4. **Python**: The programming language used to implement the crawler.

### Process Flow

1. **Initialization**:

    - The crawler initializes the MongoDB connection to store the crawled data.
    - Redis is used to initialize and manage the queue of URLs to be crawled.
    - MechanicalSoup is used as a headless browser to navigate and interact with web pages.

2. **Crawling**:

    - The crawler starts from the "Batman: Arkham Knight" page and the Steam home page.
    - For each URL, the page is downloaded and parsed for links.
    - Valid links are added to the Redis queue and stored in MongoDB.
    - The crawler keeps track of visited URLs to avoid revisiting them using a graveyard set.

3. **Path Tracking**:

    - The parent-child relationships between pages are tracked using a parent map.
    - When the "God of War" page is found, the path from the "Batman: Arkham Knight" page is reconstructed and printed.

4. **Error Handling**:
    - The crawler includes retry logic for pages that fail to load, attempting to load each page up to three times before skipping.

# Installation

1. Clone the repository to your local machine
   `git clone [repository URL]`

2. Change directory (cd) into the project folder
   `cd [project folder name]`
3. Install the required packages using pip:
   `pip install numpy opencv-python==4.7.0.68 mediapipe==0.9.0.1 scikit-learn==1.2.0`

# Create a virtual environment

python3 -m venv venv

# Activate the virtual environment

source venv/bin/activate # On macOS/Linux

# venv\Scripts\activate # On Windows

# Install pymongo with SRV support

pip install "pymongo[srv]"

# Install other dependencies

pip install mechanicalsoup redis configparser

# Run your script

python crawl.py
