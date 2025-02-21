import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.support import \
    expected_conditions as EC
import time
import requests
from datetime import datetime, timedelta
import csv
import os


class WebScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.BASE_URL = "https://bina.az"
        self.current_date = datetime.now()
        self.metro_links = []
        self.baku_region_links = []
        self.house_data = []
        self.item_ids = set()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()

    def click_element(self, by, value, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(
                (by, value))).click()

    def process_listing(self, listing):
        details = listing['Details']

        # Extract room count, area, and floor info
        room_size = details[0].split()[0] if len(
            details) > 0 else None  # Extract only the room count
        area = details[1].split()[0] if len(
            details) > 1 else None  # Extract only the area number
        floor_info = details[2] if len(
            details) > 2 else None
        current_floor, total_from = (None, None)

        # Extract current floor and total floor
        if floor_info:
            floor_parts = floor_info.split('/')
            if len(floor_parts) == 2:
                current_floor = floor_parts[
                    0].strip()  # Extract current floor number
                total_from = floor_parts[
                    1].strip()  # Extract total floors number
                total_from = total_from.split()[
                    0]

        # Translate building type
        building_type = 'old' if 'köhnə' in listing[
            'Building Type'] else 'new' if 'yeni' in \
                                           listing[
                                               'Building Type'] else None

        price_text = listing[
            'Price']  # Extracted price from HTML like '128 000'
        price = price_text.replace(' ',
                                   '')  # Remove spaces and currency

        # Prepare the data for CSV row
        return {
            'Item_id': listing['Item ID'],
            'Location1': listing['Location1'],
            'Location2': listing['Location2'],
            'room_size': room_size,
            'area': area,
            'current_floor': current_floor,
            'total_from': total_from,
            'building_type': building_type,
            'repair_status': listing['Repair Status'],
            'bill_of_sale': listing['Bill of Sale'],
            'price (AZN)': price
        }

    def scrape_metro_links(self):
        self.driver.get(self.BASE_URL)

        # Open detailed search
        self.click_element(By.XPATH,
                           '//*[@id="js-search-row-filters-btn"]')
        time.sleep(1)

        # Expand metro selection
        self.click_element(By.XPATH,
                           '//*[@id="js-search-filters-row-locations"]/div[2]/a[2]/span[1]')
        time.sleep(1)

        stations = self.driver.find_elements(By.CLASS_NAME,
                                             "search-locations__list_station")
        visited_data_ids = set()

        for station in stations:
            metro_data_id = station.get_attribute(
                "data-id")
            if metro_data_id in visited_data_ids:
                continue
            visited_data_ids.add(metro_data_id)

            station_element = self.driver.find_element(
                By.CSS_SELECTOR,
                f"span[data-id='{metro_data_id}']")
            self.driver.execute_script(
                "arguments[0].scrollIntoView();",
                station_element)
            time.sleep(0.5)
            station_element.click()

            # Apply filters
            self.click_element(By.XPATH,
                               '//*[@id="js-search-locations"]/div/div[3]/div[2]/div[2]/div[5]')
            time.sleep(1)
            self.click_element(By.XPATH,
                               '//*[@id="js-search-filters"]/div[2]/button')
            time.sleep(1)

            # Save URL
            self.metro_links.append(
                self.driver.current_url)

            # Reset for next iteration
            self._reset_search_filters()

        self._save_location_links()

    def scrape_region_links(self):
        # for testing purposes
        self.driver.get(self.BASE_URL)
        footer_locations_div = self.driver.find_element(
            By.XPATH,
            '/html/body/footer/div/div[2]/div/div[1]/div')

        # Find all <a> elements inside the div
        location_links = footer_locations_div.find_elements(
            By.TAG_NAME, 'a')

        for link in location_links:
            href = link.get_attribute('href')
            if href:
                href += "/alqi-satqi/menziller"
                self.baku_region_links.append(href)

    def _reset_search_filters(self):
        self.click_element(By.XPATH,
                           '//*[@id="js-search-row-filters-btn"]')
        time.sleep(1)
        self.click_element(By.XPATH,
                           '//*[@id="js-search-filters"]/div[2]/a[2]')
        time.sleep(1)
        self.click_element(By.XPATH,
                           '//*[@id="js-search-row-filters-btn"]')
        time.sleep(1)
        self.click_element(By.XPATH,
                           '//*[@id="js-search-filters-row-locations"]/div[2]/a[2]/span[1]')
        time.sleep(1)

    def _save_location_links(self):
        with open("location_urls.txt", "w",
                  encoding="utf-8") as file:
            for url in self.baku_region_links:
                file.write(f"{url}\n")

            for url in self.metro_links:
                file.write(f"{url}\n")

    def scrape_house_data(self):
        count = 0
        with open("location_urls.txt", "r") as f:
            links = [line.strip() for line in
                     f.readlines()]
        for base_link in links:
            page_num = 1
            while True:
                link = f"{base_link}?page={page_num}"
                print(link)
                response = requests.get(link, headers={
                    "User-Agent": "Mozilla/5.0"})
                soup = BeautifulSoup(response.text,
                                     "html.parser")

                items = soup.find_all("div",
                                      class_="items-i")
                if not items:
                    break

                page_listings = []
                count += len(items)
                for item in items:
                    listing = self._parse_listing_item(
                        item, base_link)
                    if listing:
                        page_listings.append(listing)
                if not self._process_page_listings(
                        page_listings):
                    break
                if not self._check_next_page(soup,
                                             page_num):
                    break
                page_num += 1
                print(count)

    def _parse_listing_item(self, item, base_link):
        item_link = item.find("a", class_="item_link")
        if not item_link:
            return None

        data_item_id = item_link["href"].split("/")[-1]
        if data_item_id in self.item_ids:
            return None
        self.item_ids.add(data_item_id)

        price_span = item.find("span", class_="price-val")
        price_val = price_span.text.strip() if price_span else None

        # Extract location
        # location_div = item.find("div", class_="location")
        # location = location_div.text.strip() if location_div else None
        pattern = r"baki/([^/]+)/"
        location1 = re.search(pattern, base_link).group(1)

        location_div = item.find("div", class_="location")
        location2 = location_div.text.strip() if (location_div) else None

        # Extract room count, size, and floor information
        ul_name = item.find("ul", class_="name")
        details = [li.text.strip() for li in
                   ul_name.find_all(
                       "li")] if ul_name else []
        # //*[@id="js-items-search"]/div[2]/div[1]/div[3]/div[2]
        img_tag = item.find("img")
        alt_text = img_tag.get("alt",
                               "N/A") if img_tag else "N/A"

        # Extract "category"
        match = re.search(
            r'\b(yeni tikili|köhnə tikili)\b',
            alt_text, re.IGNORECASE)
        building_type = match.group() if match else "Unknown"

        repair_div = item.find("div", class_="repair")
        repair_status = "Yes" if repair_div else "No"

        bill_of_sale_div = item.find("div",
                                     class_="bill_of_sale")
        bill_of_sale = "Yes" if bill_of_sale_div else "No"

        return {
            "Item ID": data_item_id,
            "Location1": location1,
            "Location2": location2,
            "Details": details,
            "Building Type": building_type,
            "Repair Status": repair_status,
            "Bill of Sale": bill_of_sale,
            "Price": price_val
        }

    def _process_page_listings(self, listings):
        if not listings:
            return False

        for listing in listings:
            self.house_data.append(
                self.process_listing(listing))
        return True

    def _check_next_page(self, soup, current_page):
        next_page = soup.find("a", rel="next")
        # if current_page >= 2:
        #     return False
        if len(self.house_data) < 5 and not next_page:
            return False
        return bool(next_page)

    def save_to_csv(self, filename='raw_data1.csv'):
        target_dir = os.path.join(
            os.path.dirname(os.getcwd()), 'Data')

        # if folder doesn't exist
        os.makedirs(target_dir, exist_ok=True)

        file_path = os.path.join(target_dir, filename)

        with open(file_path, 'w', newline='',
                  encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'Item_id',
                'Location1',
                'Location2',
                'room_size',
                'area',
                'current_floor',
                'total_from',
                'building_type',
                'repair_status',
                'bill_of_sale',
                'price (AZN)'
            ])
            writer.writeheader()
            writer.writerows(self.house_data)


if __name__ == "__main__":
    with WebScraper() as scraper:
        # print("Scraping region links...")
        # scraper.scrape_region_links()
        # print("Scraping metro links...")
        # scraper.scrape_metro_links()
        start_time = time.time()
        print("Scraping house data...")
        scraper.scrape_house_data()
        print("Saving data to CSV...")
        scraper.save_to_csv()
        print("Completed in"
              f" {time.time() - start_time:.2f} seconds")
