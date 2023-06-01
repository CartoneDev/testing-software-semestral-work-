import pytest
from selenium import webdriver
import time

from selenium.webdriver.common.by import By

import util


class Authentication:

    def __init__(self):
        self.remote_url = 'https://demo.prestamoduleshop.com/cs/'
        self.mail = "testo@cesto.cz"
        self.password = "testo"

    # @pytest
    def test_login_from_main_page(self):
        driver = util.get_driver("--headless")
        result = self.login(driver, self.remote_url)

        driver.close()
        assert result

    def login(self, driver, remote_url, mail=None, password=None):
        if remote_url is None:
            remote_url = self.remote_url
        if mail is None or password is None:
            mail = self.mail
            password = self.password

        driver.get(remote_url)
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


def test_login_from_main_page():
    Authentication().test_login_from_main_page()
