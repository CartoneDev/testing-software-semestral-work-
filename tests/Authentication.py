import pytest
from selenium import webdriver
import time

from selenium.webdriver.common.by import By

import util
# import os
# import sys
#
# # Get the root directory of your project
# root_dir = os.path.dirname(os.path.abspath(__file__))
#
# # Add the root directory to sys.path
# sys.path.append(root_dir)

class Authentication:
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
        self.cookie_clicker(driver)
        return self.is_authenticated(driver)

    @staticmethod
    def cookie_clicker(driver):
        cookies = driver.find_elements(By.ID, "cookie_accept")
        if len(cookies) > 0:
            cookies[0].click()

    @staticmethod
    def is_authenticated(driver):
        return len(driver.find_elements(By.CSS_SELECTOR, "a.logout")) > 0


def test_login_from_main_page(request):
    assert Authentication().test_login_from_main_page(request)
