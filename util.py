from selenium import webdriver
from selenium.webdriver.common.by import By
import os

DEBUG_ALWAYS_GUI = True


def get_driver(request, *args):
    if not request.config.getoption("--GUI"):
        args = args + ("--headless",)
    options = webdriver.FirefoxOptions()
    if "--headless" in args and not DEBUG_ALWAYS_GUI:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
    return webdriver.Firefox(options=options)


def get_data_from_csv(path_to_csv):
    import csv
    imported_data = []
    if not os.path.isfile(path_to_csv):
        return []
    with open(path_to_csv, newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in data:
            added = False
            not_empty = False
            for i, k in enumerate(row):
                if len(k) < 1 and i > 0:
                    imported_data.append(row[:i])
                    added = True
                    break
                elif i == 0 and len(k) < 1:
                    break
                else:
                    not_empty = True
            if not added and not_empty:
                imported_data.append(row)
    return imported_data


def cookie_clicker(driver):
    cookies = driver.find_elements(By.ID, "cookie_accept")
    if len(cookies) > 0:
        cookies[0].click()