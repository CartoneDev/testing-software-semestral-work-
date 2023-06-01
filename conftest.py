def pytest_addoption(parser):
    parser.addoption("--GUI", action="store_true", help="Display browser")