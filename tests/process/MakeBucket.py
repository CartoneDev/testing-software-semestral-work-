import util
import pytest
from selenium.webdriver.common.by import By

from tests.Authentication import Authentication


class BuyItems:
    def __init__(self):
        self.remote_url = 'https://demo.prestamoduleshop.com/cs/'

    def test_buy_items(self, driver):
        driver = util.get_driver("--headless")
        result = self.buy_items(driver, self.remote_url)

        driver.close()
        assert result

    def buy_items(self, driver, remote_url):
        Authentication().login(driver, remote_url)
        if not Authentication.is_authenticated(driver):
            return False
        

def test_buy_items():
    BuyItems().test_buy_items()
