from selenium.webdriver.support.wait import WebDriverWait

import util
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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

        self.open_product_page(driver, remote_url)
        product_name = self.extract_product_name(driver)

        product = {'name': product_name, 'size': 'L', 'amount': 5}

        self.selectProductSize(driver, "L")
        # self.selectProductColor(driver, "White")
        self.selectAmount(driver, 5)
        self.addToCart(driver)
        self.bucket.append(product)

        return self.bucketContainsProducts(driver)

    def open_product_page(self, driver, remote_url):
        driver.get(remote_url)
        util.cookie_clicker(driver)
        # open clothes category
        driver.find_element(By.CSS_SELECTOR, "li#category-3 > a").click()
        # open second item
        element = driver.find_element(By.XPATH, '//article[@data-id-product="2"]/div/a')
        element.click()

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
    def getAmount(driver):
        quantity = driver.find_element(By.ID, "quantity_wanted")
        return int(quantity.get_attribute("value"))

    @staticmethod
    def selectAmount(driver, param):
        quantity = driver.find_element(By.ID, "quantity_wanted")
        quantity.clear()
        quantity.send_keys(param)

    @staticmethod
    def addToCart(driver):
        add_to_cart_button = driver.find_element(By.CSS_SELECTOR, "div.add > button[type='Submit']")
        if add_to_cart_button.is_enabled():
            add_to_cart_button.click()
        else:
            return

        # wait for modal window
        while len(driver.find_elements(By.CSS_SELECTOR, "div#blockcart-modal")) == 0:
            driver.implicitly_wait(0.01)
        element = driver.find_element(By.XPATH, "//button[contains(@class, 'close')]")
        while not element.is_displayed() or not element.is_enabled():
            driver.implicitly_wait(0.01)
            element = driver.find_element(By.XPATH, "//button[contains(@class, 'close')]")
        # close modal window
        element.click()
        wait = WebDriverWait(driver, 3)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "modal")))

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

    # input changes even in case of attempt to immidiatly add to cart
    def selecting_less_than_1_items_to_add_to_bucket_test(self, driver, amount):
        self.open_product_page(driver, self.remote_url)
        self.selectAmount(driver, amount)
        # self.addToCart(driver)
        driver.find_element(By.CSS_SELECTOR, "body").click()  # emulate user activity, allowing js to update input
        return self.getAmount(driver)

    def item_overflow_in_shopping_cart_test(self, driver):
        self.clean_shopping_cart(driver)
        self.open_product_page(driver, self.remote_url)
        quantity = self.get_product_quantity(driver)
        self.selectAmount(driver, quantity + 123)
        driver.find_element(By.CSS_SELECTOR, "body").click()  # emulate user activity, allowing js to update input
        time.sleep(3)
        driver.find_element(By.CSS_SELECTOR, "body").click()  # emulate user activity, allowing js to update input
        self.addToCart(driver)

        return len(driver.find_elements(By.CSS_SELECTOR, "span#product-availability > i.product-unavailable")) > 0

    def clean_shopping_cart(self, driver):
        cart = driver.find_elements(By.CSS_SELECTOR, "div.cart > a")
        if len(cart) == 0:
            return

        cart[0].click()
        driver.find_element(By.CSS_SELECTOR, "div.blockcart a").click()
        for item in driver.find_elements(By.CSS_SELECTOR, "a.remove-from-cart"):
            item.click()

    def get_product_quantity(self, driver):
        xpath = '//a[@class="nav-link" and @data-toggle="tab" and @href="#product-details"]'
        driver.find_element(By.XPATH, xpath).click()
        quantity = driver.find_element(By.CSS_SELECTOR, "div.product-quantities > span").get_attribute("data-stock")
        return int(quantity)
