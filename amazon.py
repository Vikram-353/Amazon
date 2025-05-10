
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless browser
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Set path to your ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open Amazon search results page
search_term = "soft toys"
driver.get(f"https://www.amazon.in/s?k={search_term.replace(' ', '+')}")
time.sleep(3)  # Wait for the page to load

# Scroll down to load more products
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

# Parse page with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

# Find all product containers
products = soup.find_all("div", {"data-component-type": "s-search-result"})
print(f"Found {len(products)} products.")

# Write to CSV
with open("soft_toys.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Brand", "Reviews", "Rating", "Selling Price", "Image URL", "Product URL"])

    count = 0
    for product in products:
        try:
            title_tag = product.h2
            title = title_tag.text.strip() if title_tag else "N/A"

            link_tag = title_tag.a if title_tag and title_tag.a else None
            link = "https://www.amazon.in" + link_tag['href'] if link_tag else "N/A"

            image_tag = product.find('img')
            image = image_tag['src'] if image_tag else "N/A"

            brand_tag = product.find('span', class_='a-size-base-plus') or product.find('span', class_='a-size-base')
            brand = brand_tag.text.strip() if brand_tag else "N/A"

            rating_tag = product.select_one("span.a-icon-alt")
            rating = rating_tag.text.split()[0] if rating_tag else "N/A"

            reviews_tag = product.select_one("span.a-size-base.s-underline-text")
            reviews = reviews_tag.text.strip().replace(',', '') if reviews_tag else "0"

            price_whole = product.select_one("span.a-price-whole")
            price_frac = product.select_one("span.a-price-fraction")
            price = price_whole.text.strip()

            writer.writerow([title, brand, reviews, rating, price, image, link])
            count += 1

        except Exception as e:
            print(f"Skipping product due to error: {e}")

print(f"Scraping complete. {count} products saved to soft_toys_new.csv.")
