from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time

# 📌 Function to split product title into name & features
def split_product_title(full_title):
    lower_title = full_title.lower()

    if ' | ' in full_title:
        idx = full_title.index(' | ')
        product_name = full_title[:idx].strip()
        product_features = full_title[idx + 3:].strip()
    elif ' with ' in lower_title:
        idx = lower_title.index(' with ')
        product_name = full_title[:idx].strip()
        product_features = full_title[idx + 6:].strip()
    elif "," in full_title:
        parts = full_title.split(",", 1)
        product_name = parts[0].strip()
        product_features = parts[1].strip()
    else:
        words = full_title.split()
        product_name = " ".join(words[:5])
        product_features = " ".join(words[5:]) if len(words) > 5 else "N/A"

    return product_name, product_features

# 📌 Get product input from user
search_term = input("Enter the product name to search on Amazon.in: ")
max_pages = int(input("How many pages do you want to scrape?: "))

# 📌 Set up headless Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 📌 Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# 📌 Build Amazon search URL
search_query = search_term.replace(" ", "+")
url = f"https://www.amazon.in/s?k={search_query}"

driver.get(url)
time.sleep(3)

products = []
page_num = 1

while page_num <= max_pages:
    print(f"📖 Scraping page {page_num}...")

    items = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")

    for item in items:
        try:
            full_title = item.find_element(By.TAG_NAME, "h2").text.strip()
            product_name, product_features = split_product_title(full_title)
        except:
            product_name = "N/A"
            product_features = "N/A"

        try:
            price = item.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
        except:
            price = "N/A"

        try:
            rating_elements = item.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
            rating = rating_elements[0].get_attribute("innerHTML").strip() if rating_elements else "N/A"
        except:
            rating = "N/A"

        try:
            product_anchor = item.find_element(By.CSS_SELECTOR, "h2 a")
            product_link = product_anchor.get_attribute("href")
            if product_link and product_link.startswith("/"):
                product_link = "https://www.amazon.in" + product_link
        except:
            product_link = "N/A"

        try:
            image_url = item.find_element(By.CSS_SELECTOR, "img.s-image").get_attribute("src")
        except:
            image_url = "N/A"

        try:
            review_count_elem = item.find_elements(By.CSS_SELECTOR, "span.a-size-base.s-underline-text")
            review_count = review_count_elem[0].text.strip() if review_count_elem else "N/A"
        except:
            review_count = "N/A"

        products.append({
            "Product Name": product_name,
            "Product Features": product_features,
            "Price (₹)": price,
            "Rating": rating,
            "Reviews": review_count,
            "Product Link": product_link,
            "Image URL": image_url
        })

    # 📌 Move to next page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
        if 'disabled' in next_button.get_attribute('class'):
            print("🔚 No more pages.")
            break
        else:
            next_button.click()
            time.sleep(3)
            page_num += 1
    except NoSuchElementException:
        print("🔚 No 'Next' button. Stopping.")
        break

driver.quit()

# 📌 Save results to CSV with utf-8-sig encoding to handle ₹ symbol properly
df = pd.DataFrame(products)
csv_file_path = f"{search_term.replace(' ', '_')}_amazon_scraped_products.csv"
df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

# 📌 Success message
print(f"\n✅ Scraped {len(df)} products from {page_num} page(s) — saved to '{csv_file_path}' successfully!")
print(df.head())
