from selenium import webdriver


def get_driver(request, *args):
    if not request.config.getoption("--GUI"):
        args = args + ("--headless",)
    options = webdriver.FirefoxOptions()
    if "--headless" in args:
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
    return webdriver.Firefox(options=options)
