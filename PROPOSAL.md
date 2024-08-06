# Steam Game Path Analysis Crawl Proposal

## Objective

This crawl aims to trace the path from the "Batman: Arkham Knight" game page to the "God of War" game page on Steam by following related game links.

## Scope

The crawl will focus on the following key pieces of information for each game page visited:

1. Game Title
2. URL
3. Related Games (and their URLs)

## Data Sources and Endpoints

1. **Initial Game Page**: "Batman: Arkham Knight"
    - URL: `https://store.steampowered.com/app/208650/Batman_Arkham_Knight/`
2. **Endpoint Game Page**: "God of War"
    - URL: `https://store.steampowered.com/app/1593500/God_of_War/`

# Navigate to your project directory

cd /path/to/your/project

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
