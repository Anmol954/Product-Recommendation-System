import pandas as pd
import time
import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

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

def scrape_amazon_products(search_term, max_pages=1):
    chrome_options = Options()

    # Detect platform
    chrome_options = Options()
    if platform.system() == "Linux":
        chrome_options.binary_location = "/usr/bin/google-chrome"

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    search_query = search_term.replace(" ", "+")
    url = f"https://www.amazon.in/s?k={search_query}"

    driver.get(url)
    time.sleep(3)

    products = []
    page_num = 1

    while page_num <= max_pages:
        items = driver.find_elements(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        for item in items:
            try:
                full_title = item.find_element(By.TAG_NAME, "h2").text.strip()
                product_name, product_features = split_product_title(full_title)
            except:
                product_name, product_features = "N/A", "N/A"

            try:
                price = item.find_element(By.CSS_SELECTOR, "span.a-price-whole").text.strip()
            except:
                price = "0"

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
                review_count = review_count_elem[0].text.strip() if review_count_elem else "0"
            except:
                review_count = "0"

            products.append({
                "Product Name": product_name,
                "Product Features": product_features,
                "Price (₹)": price,
                "Rating": rating,
                "Reviews": review_count,
                "Product Link": product_link,
                "Image URL": image_url
            })

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
            if 'disabled' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(2)
            page_num += 1
        except NoSuchElementException:
            break

    driver.quit()
    return pd.DataFrame(products)
