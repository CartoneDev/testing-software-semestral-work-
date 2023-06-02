import time

from selenium.webdriver.common.by import By
import util

class Search:
    """ Provides a complex sequential test of adding items to the bucket and checking the bucket content."""
    def __init__(self):
        self.remote_url = 'https://demo.prestamoduleshop.com/cs/'
        self.bucket = []

    def test_search_by(self, driver, query, expected_products):
        driver.get(self.remote_url)
        util.cookie_clicker(driver)
        search_input = driver.find_element(By.CSS_SELECTOR, "input[name='s']")
        search_input.clear()
        search_input.send_keys(query)
        search_input.submit()
        time.sleep(4)  # wait for the page to load
        items = driver.find_elements(By.CSS_SELECTOR, "article.product-miniature")
        if expected_products is None:
            return len(items) == 0
        if len(items) < len(expected_products):
            return False
        titles = [self.extract_title(item) for item in items]
        for product in expected_products:
            if product not in titles:
                return False

        return True

    @staticmethod
    def extract_title(item):
        return item.find_element(By.CSS_SELECTOR, "h2.product-title a").text

