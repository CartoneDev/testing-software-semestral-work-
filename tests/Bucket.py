import random

from selenium.webdriver import Keys

import util
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.ui as ui
import selenium
import selenium.webdriver.common.alert

from tests.Account import Account


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

        if not Account.is_authenticated(driver):
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
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "select[name='group[1]']")))
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

    def test_different_shipping_methods(self, driver, shipping):
        acc = Account()
        acc.ensure_login(driver)
        if not acc.is_authenticated(driver):
            return False
        self.open_product_page(driver, self.remote_url)
        self.selectProductSize(driver, "M")
        self.selectAmount(driver, random.randint(1, 3))
        self.addToCart(driver)
        wait = WebDriverWait(driver, 15)

        driver.execute_script("Object.defineProperty(navigator, 'geolocation', {value: {}});")

        # Refresh the page to trigger the location access prompt
        driver.refresh()

        cart_btn = driver.find_element(By.CSS_SELECTOR, "div.blockcart a")
        wait.until(EC.element_to_be_clickable(cart_btn))
        driver.execute_script("arguments[0].scrollIntoView();", cart_btn)
        driver.execute_script("arguments[0].click();", cart_btn)  # bypass modal disappearing tho blocking cart issue
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.checkout a.btn-primary")))
        driver.find_element(By.CSS_SELECTOR, "div.checkout a.btn-primary").click()
        overlay = driver.find_element(By.CSS_SELECTOR, "div.myOverlayBlock")
        wait.until(EC.invisibility_of_element(overlay))
        submitBtn = driver.find_element(By.XPATH,
                                        '//button[@name="confirm-addresses" and contains(text(), "Pokračovat")]')
        wait.until(EC.element_to_be_clickable(submitBtn))
        submitBtn.click()
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.myOverlayBlock")))
        time.sleep(0.2)
        self.selectDelivery(driver, shipping)
        self.selectPaymentAndPay(driver)
        return self.verifyOrderSuccess(driver)

    def selectDelivery(self, driver, shipping):
        service = shipping["service"]

        if service == "post":
            pass  # default
        elif service == "zasilkovna":
            self.selectZasilkovna(driver, shipping["branch"])
        elif service == "ppl":
            self.selectPPL(driver, shipping["branch"])
        elif service == "balik":
            self.selectBalik(driver, shipping["branch"])
        elif service == "post_local":
            self.selectLocalPost(driver, shipping["branch"])
        time.sleep(0.3)
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[name=confirmDeliveryOption]")))
        opt = driver.find_element(By.CSS_SELECTOR, "button[name=confirmDeliveryOption]")
        driver.execute_script("arguments[0].click();", opt)  # bypass some interception

    def selectPaymentAndPay(self, driver):
        wait = WebDriverWait(driver, 20)
        wait.until(EC.invisibility_of_element((By.CSS_SELECTOR, "div.myOverlayBlock")))
        c = driver.find_elements(By.CSS_SELECTOR, "div.myRippleBlock")
        while len(c) > 0 and c[0].is_displayed():
            # meh, wait until won't do for this
            time.sleep(0.1)
            c = driver.find_elements(By.CSS_SELECTOR, "div.myRippleBlock")
        time.sleep(1)

        while len(driver.find_elements(By.CSS_SELECTOR, "input#payment-option-1")) == 0:
            time.sleep(0.1)
        time.sleep(1)
        opt = driver.find_element(By.CSS_SELECTOR, "input#payment-option-1")
        driver.execute_script("arguments[0].click();", opt)  # bypass some interception
        opt = driver.find_element(By.XPATH, "//input[@id='conditions_to_approve[terms-and-conditions]']")
        driver.execute_script("arguments[0].click();", opt)  # bypass some interception
        opt = driver.find_element(By.CSS_SELECTOR, "div#payment-confirmation button")
        driver.execute_script("arguments[0].click();", opt)  # bypass some interception

    def selectZasilkovna(self, driver, branch):
        driver.find_element(By.CSS_SELECTOR, "input#delivery_option_32").click()
        wait = WebDriverWait(driver, 35)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button#open-packeta-widget")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#open-packeta-widget")))
        driver.execute_script("arguments[0].click();", driver.find_element(By.CSS_SELECTOR,
                                                                           "button#open-packeta-widget"))  # bypass some interception

        frame_locator = (By.XPATH, "//iframe[@id='packeta-widget']")
        wait.until(EC.frame_to_be_available_and_switch_to_it(frame_locator))
        cookiePth = '//button[@data-cookiefirst-action="accept" and @tabindex="1" and ' \
                 '@data-cookiefirst-outline-accent-color="true" and @data-cookiefirst-button="primary"] '


        cookie = driver.find_elements(By.XPATH, cookiePth)
        if len(cookie) > 0:
            cookie[0].click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#custom-autocomplete")))
        input = driver.find_element(By.CSS_SELECTOR, "input#custom-autocomplete")

        input.send_keys(branch)
        input.send_keys(Keys.DOWN)
        input.send_keys(Keys.ENTER)
        cookie = driver.find_elements(By.XPATH, cookiePth)
        if len(cookie) > 0:
            cookie[0].click()
        wait.until(EC.visibility_of_any_elements_located(
            (By.CSS_SELECTOR, 'div.branch-list div.branch-list-item:first-child')))
        cookie = driver.find_elements(By.XPATH, cookiePth)
        if len(cookie) > 0:
            cookie[0].click()
        branch_to_select = driver.find_element(By.CSS_SELECTOR, 'div.branch-list div.branch-list-item:first-child')
        branch_to_select.click()
        while len(driver.find_elements(By.CSS_SELECTOR, "button#btn_select_branch")) == 0:
            time.sleep(0.02)
        submit = driver.find_element(By.CSS_SELECTOR, 'div.select-container button#btn_select_branch')
        submit.click()
        driver.switch_to.default_content()

    def verifyOrderSuccess(self, driver):
        return len(driver.find_elements(By.CSS_SELECTOR, 'i.material-icons.rtl-no-flip.done')) > 0

    def selectPPL(self, driver, delivery):
        driver.find_element(By.CSS_SELECTOR, "input#delivery_option_37").click()
        wait = WebDriverWait(driver, 15)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.selection > span > span")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.selection > span > span")))
        driver.find_element(By.CSS_SELECTOR, "span.selection > span > span").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))

        input_field = driver.find_element(By.CSS_SELECTOR, "input.select2-search__field")
        input_field.send_keys(delivery)
        input_field.send_keys(Keys.ENTER)

    def selectBalik(self, driver, delivery_address):
        driver.find_element(By.CSS_SELECTOR, "input#delivery_option_34").click()
        wait = WebDriverWait(driver, 15)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.selection > span > span")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.selection > span > span")))

        while len(driver.find_elements(By.CSS_SELECTOR, "span.selection div.address")) == 0:
            driver.find_element(By.CSS_SELECTOR, "span.selection > span > span").click()
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))
            input_field = driver.find_element(By.CSS_SELECTOR, "input.select2-search__field")
            input_field.send_keys("!@#DSQSEARCHNOTSEARCHNOTSEARCHNOT")
            input_field.clear()
            input_field.send_keys(delivery_address)
            result_list_locator = (By.CSS_SELECTOR, '.select2-results__options li.select2-results__option')
            wait.until(EC.presence_of_all_elements_located(result_list_locator))
            input_field.send_keys(Keys.ENTER)
            time.sleep(0.123)

    def selectLocalPost(self, driver, param):
        driver.find_element(By.CSS_SELECTOR, "input#delivery_option_17").click()
        wait = WebDriverWait(driver, 15)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "span.selection > span > span")))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.selection > span > span")))
        driver.execute_script("arguments[0].scrollIntoView();", driver.find_element(By.CSS_SELECTOR,
                                                                                    "span.selection > span > span"))
        driver.find_element(By.CSS_SELECTOR, "span.selection > span > span").click()

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))

        while not self.addressSelected(driver, param):
            input_field = self.find_or_create_input(driver)
            input_field.send_keys(param)
            while not self.first_option_for_selection_contains(driver, param):
                time.sleep(0.123)
            self.select_first_option(driver)

    def addressSelected(self, driver, param):
        return len(driver.find_elements(By.CSS_SELECTOR, "span.selection div.address")) > 0

    def find_or_create_input(self, driver):
        elems = driver.find_elements(By.CSS_SELECTOR, "input.select2-search__field")
        if len(elems) > 0:
            return elems[0]
        else:
            driver.find_element(By.CSS_SELECTOR, "span.selection > span > span").click()
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))
            return driver.find_element(By.CSS_SELECTOR, "input.select2-search__field")

    def first_option_for_selection_contains(self, driver, param):
        result_list_locator = (By.CSS_SELECTOR, '.select2-results__options li.select2-results__option')
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_all_elements_located(result_list_locator))
        first_option = driver.find_element(By.CSS_SELECTOR,
                                           '.select2-results__options li.select2-results__option:first-child')
        text = first_option.text
        return param.lower() in text.lower()

    def select_first_option(self, driver):
        wait = WebDriverWait(driver, 30)
        first_option = driver.find_element(By.CSS_SELECTOR,
                                           '.select2-results__options li.select2-results__option:first-child')
        wait.until(EC.element_to_be_clickable(first_option))

        first_option.click()
