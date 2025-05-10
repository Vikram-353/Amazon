# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# import time

# # Initialize driver
# options = webdriver.ChromeOptions()
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("start-maximized")
# options.add_argument("disable-infobars")
# options.add_argument("--disable-extensions")
# # options.add_argument("--headless")  # Headless mode
# options.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
# )
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # Go to Amazon India
# url = "https://www.amazon.in/Storio-Super-Plushie-Plush-Girls/dp/B0CQG69GBY/ref=sxin_15_pa_sp_search_thematic_sspa?content-id=amzn1.sym.70fd741c-68a9-470a-9805-115e3115104d%3Aamzn1.sym.70fd741c-68a9-470a-9805-115e3115104d&crid=25XHQ7HJKKUSV&cv_ct_cx=soft+toys&keywords=soft+toys&pd_rd_i=B0CQG69GBY&pd_rd_r=8eec95ed-a574-4947-89e8-0c56cebf6d08&pd_rd_w=HIzv8&pd_rd_wg=loVB8&pf_rd_p=70fd741c-68a9-470a-9805-115e3115104d&pf_rd_r=QB5S1PCK7YG7D6MQQF3K&qid=1746879356&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sprefix=soft+toy%2Caps%2C262&sr=1-1-66673dcf-083f-43ba-b782-d4a436cc5cfb-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9zZWFyY2hfdGhlbWF0aWM&psc=1"
# driver.get(url)
# time.sleep(5)

# # Scroll to load content
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# time.sleep(5)

# # Parse HTML
# soup = BeautifulSoup(driver.page_source, 'html.parser')
# products = soup.find_all('div', {'data-component-type': 's-search-result'})

# # Prepare text output
# output_lines = []

# for product in products:
#     if product.select_one("span.s-sponsored-label-text"):
#         try:
#             title = product.h2.text.strip()
#             link = "https://www.amazon.in" + product.h2.a['href']
#             image = product.find('img')['src']
#             brand = product.find('span', class_='a-size-base-plus') or product.find('span', class_='a-size-base')
#             brand = brand.text.strip() if brand else "N/A"
#             rating_tag = product.select_one("span.a-icon-alt")
#             rating = rating_tag.text.split()[0] if rating_tag else "N/A"
#             reviews_tag = product.select_one("span.a-size-base.s-underline-text")
#             reviews = reviews_tag.text.strip().replace(',', '') if reviews_tag else "0"
#             price_whole = product.select_one("span.a-price-whole")
#             price_frac = product.select_one("span.a-price-fraction")
#             price = f"₹{price_whole.text.strip()}.{price_frac.text.strip()}" if price_whole and price_frac else "N/A"

#             # Format the product info
#             product_info = (
#                 f"Title: {title}\n"
#                 f"Brand: {brand}\n"
#                 f"Reviews: {reviews}\n"
#                 f"Rating: {rating}\n"
#                 f"Selling Price: {price}\n"
#                 f"Image URL: {image}\n"
#                 f"Product URL: {link}\n"
#                 "-----------------------------\n"
#             )
#             output_lines.append(product_info)
#             print(product_info)  # Print to terminal

#         except Exception as e:
#             print(f"Skipping a product due to error: {e}")

# # Save to .txt file
# with open("sponsored_soft_toys.txt", "w", encoding="utf-8") as file:
#     file.writelines(output_lines)

# print("Scraping complete. Data saved to sponsored_soft_toys.txt.")

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
