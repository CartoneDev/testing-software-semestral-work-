

def pytest_addoption(parser):
    parser.addoption("--GUI", action="store_true", help="Display browser")


# def pytest_runtest_protocol(item, nextitem):
#     outcome = yield
#     result = outcome.get_result()
#     if result.passed and nextitem is None:
#         # Perform teardown steps after all tests pass
#         # This code block will only execute once after all tests have completed successfully
#         print("Performing teardown steps after all tests pass")