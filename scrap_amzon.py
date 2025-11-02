import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime, timezone
from itertools import zip_longest


Title = []
price = []
link = []
Availability = []
star = []
source_page = []
scraped_at = []

now_utc = datetime.now(timezone.utc)

for i in range(1, 51):
    response = requests.get(f"https://books.toscrape.com/catalogue/page-{i}.html")
    soup = BeautifulSoup(response.content, "lxml")

    def fetch_rating(s):
        a = ""
        for i in str(s):
            if i != '\n':
                a += i
            else:
                break
        a = a.split()
        a = a[-1][:-2]
        return a

    books = soup.find_all("li", {"class":"col-xs-6 col-sm-4 col-md-3 col-lg-3"})
    for book in books:
        formatted_time = now_utc.strftime("%Y/%m/%d %H:%M:%S")
        scraped_at.append(formatted_time)
        source_page.append(f"https://books.toscrape.com/catalogue/page-{i}.html")
        Title.append(book.find("h3").find("a")["title"])
        price.append(book.find("p", {"class":"price_color"}).text)
        link.append(book.find("h3").find("a")["href"])
        Availability.append(book.find("p", {"class", "instock availability"}).text.strip())
        star.append(fetch_rating(book.find("p", {"class": "star-rating"})))

    file_list = [scraped_at, Title, price, Availability, star, link, source_page]
    exported = zip_longest(*file_list)

with open("/goinfre/hrami/python/webscraping/file.csv", "w") as mfile:
    wr = csv.writer(mfile)
    wr.writerow(["scraped_at", "Title", "Price", "Availability", "Star", "Link", "source page"])
    wr.writerows(exported)
