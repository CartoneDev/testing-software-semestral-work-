import pytest
from selenium import webdriver
import time

from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
import util


# import os
# import sys
#
# # Get the root directory of your project
# root_dir = os.path.dirname(os.path.abspath(__file__))
#
# # Add the root directory to sys.path
# sys.path.append(root_dir)

class Account:
    """ Tests if logining is possible [for a given user.]"""

    def __init__(self):
        self.remote_url = 'https://demo.prestamoduleshop.com/cs/'
        self.mail = "testo@cesto.cz"
        self.password = "testo"

    # @pytest
    def test_login_from_main_page(self, driver, mail=None, password=None):
        result = self.login(driver, self.remote_url, mail, password)
        return result

    def login(self, driver, remote_url, mail=None, password=None):
        if remote_url is None:
            remote_url = self.remote_url
        if mail is None or password is None:
            mail = self.mail
            password = self.password

        driver.get(remote_url)
        util.cookie_clicker(driver)
        button = driver.find_element(By.CSS_SELECTOR, "div.user-info > a")
        button.click()
        mail_input_field = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
        mail_input_field.clear()
        mail_input_field.send_keys(mail)
        password_input_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input_field.clear()
        password_input_field.send_keys(password)
        login_button = driver.find_element(By.ID, "submit-login")
        login_button.click()
        return self.is_authenticated(driver)

    @staticmethod
    def is_authenticated(driver):
        return len(driver.find_elements(By.CSS_SELECTOR, "a.logout")) > 0

    def ensure_login(self, driver):
        if not self.is_authenticated(driver):
            self.login(driver, self.remote_url)

    def test_address_change(self, driver, new_address="Prague"):
        self.ensure_login(driver)
        if not self.is_authenticated(driver):
            return False
        driver.get(self.remote_url)
        util.cookie_clicker(driver)
        driver.find_element(By.CSS_SELECTOR, "a.account").click()
        driver.find_element(By.CSS_SELECTOR, "a#addresses-link").click()
        addresses = driver.find_elements(By.XPATH, "//a[contains(@data-link-action, 'edit-address')]")
        if len(addresses) == 0:
            return False
        addresses[0].click()
        address_input = driver.find_element(By.CSS_SELECTOR, "input[name='address1']")
        address_input.clear()
        address_input.send_keys(new_address)
        psc = driver.find_element(By.CSS_SELECTOR, "input[name='postcode']")
        psc_val = psc.get_attribute("value")
        psc.clear()
        psc_new_val = psc_val[:3].strip() + " " + psc_val[3:].strip()
        psc.send_keys(psc_new_val)
        save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.float-xs-right")
        save_button.click()
        return len(driver.find_elements(By.CSS_SELECTOR, 'article.alert.alert-success[data-alert="success"]')) > 0

    def test_name_change_contains_digits(self, driver):
        self.ensure_login(driver)
        if not self.is_authenticated(driver):
            return False
        driver.get(self.remote_url)
        util.cookie_clicker(driver)
        driver.find_element(By.CSS_SELECTOR, "a.account").click()
        driver.find_element(By.CSS_SELECTOR, "a#identity-link").click()
        first_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='firstname']")
        first_name_input.clear()
        first_name_input.send_keys("123 test 123")
        gdpr_checkbox = driver.find_element(By.CSS_SELECTOR, "input[name='gdpr_approval']")
        gdpr_checkbox.click()
        save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.float-xs-right")
        save_button.click()
        elements = driver.find_elements(By.XPATH,
                                        '//input[@name="firstname"]/following-sibling::div[@class="help-block"]/ul/li[@class="alert alert-danger"]')
        return len(elements) > 0

    def test_change_mail(self, driver):
        self.ensure_login(driver)
        if not self.is_authenticated(driver):
            return False
        driver.get(self.remote_url)
        util.cookie_clicker(driver)
        driver.find_element(By.CSS_SELECTOR, "a.account").click()
        driver.find_element(By.CSS_SELECTOR, "a#identity-link").click()
        mail_input = driver.find_element(By.CSS_SELECTOR, "input[name='email']")
        mail_input.clear()
        mail_input.send_keys("notamail.com")
        gdpr_checkbox = driver.find_element(By.CSS_SELECTOR, "input[name='gdpr_approval']")
        gdpr_checkbox.click()
        save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.float-xs-right")
        save_button.click()
        time.sleep(0.1)
        return mail_input == driver.switch_to.active_element

    def test_change_personal_info(self, driver, user_info):
        self.ensure_login(driver)
        if not self.is_authenticated(driver):
            return False
        driver.get(self.remote_url)
        util.cookie_clicker(driver)
        driver.find_element(By.CSS_SELECTOR, "a.account").click()
        driver.find_element(By.CSS_SELECTOR, "a#identity-link").click()
        self.fill_form(driver, user_info)
        success = len(driver.find_elements(By.CSS_SELECTOR, 'article.alert.alert-success[data-alert="success"]')) > 0

        return success == (user_info['result'] == '1')

    def fill_form(self, driver, user_info):
        self.enter_firstname_if_present(driver, user_info)
        self.enter_lastname_if_present(driver, user_info)
        self.enter_date_of_birth_if_present(driver, user_info)
        self.fill_password(driver)
        gdpr_checkbox = driver.find_element(By.CSS_SELECTOR, "input[name='gdpr_approval']")
        gdpr_checkbox.click()
        save_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.float-xs-right")
        save_button.click()

    @staticmethod
    def enter_lastname_if_present(driver, obj_dict):
        if "lastname" not in obj_dict.keys():
            return
        last_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='lastname']")
        last_name_input.clear()
        last_name_input.send_keys(obj_dict["lastname"])

    def enter_firstname_if_present(self, driver, obj_dict):
        if "firstname" not in obj_dict.keys():
            return
        first_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='firstname']")
        first_name_input.clear()
        first_name_input.send_keys(obj_dict["firstname"])

    def enter_date_of_birth_if_present(self, driver, obj_dict):
        if "date" not in obj_dict.keys():
            return
        first_name_input = driver.find_element(By.CSS_SELECTOR, "input[name='birthday']")
        first_name_input.clear()
        first_name_input.send_keys(obj_dict["date"])

    def fill_password(self, driver):
        password_input_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
        password_input_field.clear()
        password_input_field.send_keys(self.password)
        password_input_field = driver.find_element(By.CSS_SELECTOR, "input[name='new_password']")
        password_input_field.clear()
        password_input_field.send_keys(self.password)
