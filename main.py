from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Chrome with visible browser (not headless for debugging)
options = webdriver.ChromeOptions()
# Comment out headless to debug visually
# options.add_argument("--headless")
options.add_argument("--start-maximized")
options.add_argument('--disable-blink-features=AutomationControlled')

# Initialize driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Amazon search page
url = "https://www.amazon.in/s?k=soft+toys"
driver.get(url)

# Wait until products are loaded
WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.s-main-slot"))
)

# Scroll down to load sponsored ads
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(5)

# Parse HTML
soup = BeautifulSoup(driver.page_source, 'html.parser')
products = soup.find_all('div', {'data-component-type': 's-search-result'})

# Data list
data = []

for product in products:
    # Check if sponsored
    sponsored_label = product.select_one("span.s-sponsored-label-text")
    if sponsored_label:
        try:
            title_tag = product.h2.a
            title = title_tag.text.strip()
            product_url = "https://www.amazon.in" + title_tag['href']

            image_tag = product.find('img')
            image_url = image_tag['src'] if image_tag else "N/A"

            brand_tag = product.find('h5') or product.find('span', class_='a-size-base-plus')
            brand = brand_tag.text.strip() if brand_tag else "N/A"

            rating_tag = product.select_one("span.a-icon-alt")
            rating = rating_tag.text.split()[0] if rating_tag else "N/A"

            reviews_tag = product.select_one("span.a-size-base.s-underline-text")
            reviews = reviews_tag.text.strip().replace(',', '') if reviews_tag else "0"

            price_whole = product.select_one("span.a-price-whole")
            price_frac = product.select_one("span.a-price-fraction")
            price = f"₹{price_whole.text}.{price_frac.text}" if price_whole and price_frac else "N/A"

            # Append to list
            data.append({
                "Title": title,
                "Brand": brand,
                "Reviews": reviews,
                "Rating": rating,
                "Selling Price": price,
                "Image URL": image_url,
                "Product URL": product_url
            })

        except Exception as e:
            print("Error parsing a product:", e)

# Save data
df = pd.DataFrame(data)
df.to_csv("sponsored_soft_toys.csv", index=False)
print(f"{len(df)} sponsored products scraped and saved to sponsored_soft_toys.csv")

# Cleanup
driver.quit()
