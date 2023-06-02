import util
import pytest
import time
from selenium.webdriver.common.by import By

from tests.Authentication import Authentication


class Bucket:
    """ Provides a complex sequential test of adding items to the bucket and checking the bucket content."""

    def __init__(self):
        self.remote_url = 'https://demo.prestamoduleshop.com/cs/'
        self.bucket = []

    def items_adds_to_bucket_test(self, driver):
        result = self.bucket_items(driver, self.remote_url)
        return result

    def bucket_items(self, driver, remote_url):
        if remote_url is None:
            remote_url = self.remote_url
        if driver is None:
            return False

        if not Authentication.is_authenticated(driver):
            return False

        driver.get(remote_url)
        # open clothes category
        driver.find_element(By.CSS_SELECTOR, "li#category-3 > a").click()

        # open second item
        element = driver.find_element(By.XPATH, '//article[@data-id-product="2"]/div/a')
        element.click()
        product_name = self.extract_product_name(driver)

        product = {'name': product_name, 'size': 'L', 'amount': 5}

        self.selectProductSize(driver, "L")
        # self.selectProductColor(driver, "White")
        self.selectAmount(driver, 5)
        self.addToCart(driver)
        self.bucket.append(product)

        return self.bucketContainsProducts(driver)

    @staticmethod
    def selectProductSize(driver, size):
        # select size
        size_select = driver.find_element(By.CSS_SELECTOR, "select[name='group[1]']")
        size_select.click()
        size_select.find_element(By.XPATH, "//option[. = '" + size + "']").click()

    @staticmethod
    def selectProductColor(driver, color):
        # select color
        color_value = color == 'White' and '8' or '11'
        xpath_expression = f"//input[@class='input-color' and @value='{color_value}']"
        color_select = driver.find_element(By.XPATH, xpath_expression)
        color_select.click()

    @staticmethod
    def selectAmount(driver, param):
        quantity = driver.find_element(By.ID, "quantity_wanted")
        quantity.clear()
        quantity.send_keys(param)

    @staticmethod
    def addToCart(driver):
        add_to_cart_button = driver.find_element(By.CSS_SELECTOR, "div.add > button[type='Submit']")
        add_to_cart_button.click()

        # wait for modal window
        while len(driver.find_elements(By.CSS_SELECTOR, "div#blockcart-modal")) == 0:
            time.sleep(4)
        # close modal window
        driver.find_element(By.XPATH, "//button[contains(@class, 'close')]").click()

    @staticmethod
    def extract_product_name(driver):
        element = driver.find_element(By.XPATH, "(//a[@itemprop='item']/span[@itemprop='name'])[last()]")
        return element.text

    def bucketContainsProducts(self, driver):
        # reduce products if added multiple times
        reduced_products = {}
        for product in self.bucket:
            key = (product["name"], product["size"])
            if key in reduced_products:
                reduced_products[key]["amount"] += product["amount"]
            else:
                reduced_products[key] = product
        self.bucket = reduced_products.values()
        time.sleep(1)  # wait for cart to update and modal window to close
        driver.find_element(By.CSS_SELECTOR, "div.blockcart a").click()
        items = driver.find_elements(By.CSS_SELECTOR, "li.cart-item")
        items_as_products = self.to_products(items)
        result = True
        for product in self.bucket:
            result = result and product in items_as_products
        return result

    @staticmethod
    def to_products(items):
        products = []
        for item in items:
            name = item.find_element(By.CSS_SELECTOR, "div.product-line-info > a").text
            size = item.find_element(By.CSS_SELECTOR, "div.product-line-info > span.value").text
            amountElem = item.find_element(By.CSS_SELECTOR, "input.js-cart-line-product-quantity")
            amount = int(amountElem.get_attribute("value"))
            products.append({'name': name, 'size': size, 'amount': amount})
        return products

