# Import the HTTP client for fetching web pages
import requests
# Import the HTML parser to navigate and extract elements
from bs4 import BeautifulSoup
# Import CSV utilities for saving tabular data
import csv
# Import time utilities to generate a timestamp for each row
from datetime import datetime, timezone
# Utility to transpose lists-of-columns into rows when lengths match
from itertools import zip_longest

# Lists to collect columnar data for each scraped book
Title = []          # Book titles (strings)
price = []          # Price strings as shown on site (e.g., "£51.77")
link = []           # Product page links (relative URLs from listing page)
Availability = []   # Availability text (e.g., "In stock")
star = []           # Star ratings (e.g., "Three")
source_page = []    # Which listing page URL each item came from
scraped_at = []     # Run timestamp per row (same for entire run or page)

# Capture the current UTC time once for this run
now_utc = datetime.now(timezone.utc)

# Loop through all 50 catalogue pages
for i in range(1, 51):
    # Build the page URL for the current page index
    page_url = f"https://books.toscrape.com/catalogue/page-{i}.html"

    # Fetch the page content (basic GET; consider adding headers + timeout in production)
    response = requests.get(page_url)

    # Parse the HTML using lxml parser for speed/robustness
    soup = BeautifulSoup(response.content, "lxml")

    # Helper function to parse the rating from the star-rating <p> tag
    # Note: This mimics your approach; alternatively, one could read classes and map words to numbers.
    def fetch_rating(s):
        # Accumulate characters until a newline, then stop
        a = ""
        for ch in str(s):
            if ch != '\n':
                a += ch
            else:
                break
        # Split the accumulated string into tokens
        a = a.split()
        # Take the last token, chop last two chars (e.g., 'Three">' -> 'Three')
        a = a[-1][:-2]
        return a

    # Select all book cards by their grid item class
    books = soup.find_all("li", {"class": "col-xs-6 col-sm-4 col-md-3 col-lg-3"})

    # Iterate through each book card and extract fields
    for book in books:
        # Format a consistent timestamp string for provenance (UTC)
        formatted_time = now_utc.strftime("%Y/%m/%d %H:%M:%S")
        scraped_at.append(formatted_time)            # Store timestamp per row
        source_page.append(page_url)                 # Store which page produced this row

        # Title is stored on the anchor inside the h3 as the 'title' attribute
        Title.append(book.find("h3").find("a")["title"])

        # Extract the price text, e.g., "£51.77"
        price.append(book.find("p", {"class": "price_color"}).get_text(strip=True))

        # Extract the relative product link from the anchor in the h3
        link.append(book.find("h3").find("a")["href"])

        # Extract availability text; fix selector to a proper dict or use CSS
        # Using CSS-style: p with both classes 'instock' and 'availability'
        Availability.append(
            book.select_one("p.instock.availability").get_text(strip=True)
        )

        # Extract the star rating from the 'star-rating' <p> element
        star.append(fetch_rating(book.find("p", {"class": "star-rating"})))

    # After finishing the current page, prepare a rows iterator from column lists
    # (We reassign on each page but only write once after loop; keeping this here mirrors your structure.)
    file_list = [scraped_at, Title, price, Availability, star, link, source_page]
    exported = zip_longest(*file_list)

# Open the output CSV (write mode). Consider newline='' and encoding='utf-8' for portability.
with open("/goinfre/hrami/python/webscraping/file.csv", "w", newline="", encoding="utf-8") as mfile:
    # Create a CSV writer
    wr = csv.writer(mfile)
    # Write header row with column names
    wr.writerow(["scraped_at", "Title", "Price", "Availability", "Star", "Link", "source page"])
    # Write all data rows produced by zipping the lists
    wr.writerows(exported)
