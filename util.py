from selenium import webdriver
from selenium.webdriver.common.by import By
import os

DEBUG_ALWAYS_GUI = False


def get_driver(request, *args):
    if not request.config.getoption("--GUI"):
        args = args + ("--headless",)
    options = webdriver.FirefoxOptions()
    options.set_preference("geo.enabled", True)
    options.set_preference("geo.provider.use_corelocation", True)
    options.set_preference("geo.prompt.testing", True)
    options.set_preference("geo.prompt.testing.allow", True)
    if "--headless" in args and not DEBUG_ALWAYS_GUI:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
    return webdriver.Firefox(options=options)


def get_data_from_csv(path_to_csv, stop_on_empty=True):
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
                if len(k) < 1 and i > 0 and stop_on_empty:
                    imported_data.append(row[:i])
                    added = True
                    break
                elif i == 0 and len(k) < 1 and stop_on_empty:
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


def parse_csv_to_objects(csv_data):
    naming = {}
    resulting_objects = []
    for i, row in enumerate(csv_data):
        object = {}
        for j, cell in enumerate(row):
            if i == 0 and len(cell) > 0:
                naming[j] = cell
            elif i > 0 and j in naming and len(cell) > 0:
                object[naming[j]] = cell
        if len(object) > 0:
            resulting_objects.append(object)

    return resulting_objects


def switch_to_iframe(driver, iframe):
    return driver.switch_to.frame(iframe)