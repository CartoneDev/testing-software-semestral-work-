import pytest
import util
from tests.Authentication import Authentication
from tests.process.Bucket import Bucket


@pytest.fixture(scope='session', autouse=True, name='driver')
def shared_data(request):
    driver = util.get_driver(request, "")
    yield driver
    driver.close()


@pytest.mark.run(order=1)
def test_login_from_main_page(driver):
    assert Authentication().test_login_from_main_page(driver)


def test_bucket_items(driver):
    Bucket().items_adds_to_bucket_test(driver)
