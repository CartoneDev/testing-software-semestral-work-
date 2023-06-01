import selenium


def get_driver(*args):
    options = selenium.webdriver.ChromeOptions()
    if "--headless" in args:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
    return selenium.webdriver.Chrome(options=options)
