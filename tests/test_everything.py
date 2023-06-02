import pytest
import util
from tests.Authentication import Authentication
from tests.Bucket import Bucket
from tests.Search import Search


@pytest.fixture(scope='session', autouse=True, name='driver')
def shared_data(request):
    driver = util.get_driver(request, "")
    yield driver
    driver.close()


@pytest.mark.run(order=1)
def test_login_from_main_page(driver):
    assert Authentication().test_login_from_main_page(driver)


@pytest.mark.run(order=2)
def test_bucket_items(driver):
    assert Bucket().items_adds_to_bucket_test(driver)


def test_item_overflow_in_shopping_cart(driver):
    assert Bucket().item_overflow_in_shopping_cart_test(driver)


def test_selecting_less_than_1_items_to_add_to_bucket(driver):
    assert Bucket().selecting_less_than_1_items_to_add_to_bucket_test(driver, -1) > 0
    assert Bucket().selecting_less_than_1_items_to_add_to_bucket_test(driver, 0) > 0
    assert Bucket().selecting_less_than_1_items_to_add_to_bucket_test(driver, -128) > 0
    assert Bucket().selecting_less_than_1_items_to_add_to_bucket_test(driver, -325) > 0


def test_search(driver):
    assert Search().test_search_by(driver, "brown",
                                   ["Brown Bear Cushion", "Brown Bear Notebook", "Brown Bear + Video Product"])


@pytest.mark.parametrize("path_to_csv", ["tests/data/search.csv", "data/search.csv"])
def test_search_by_csv_provided_data(driver, path_to_csv):
    csv_data = util.get_data_from_csv(path_to_csv)
    for row in csv_data:
        assert Search().test_search_by(driver, row[0], row[1:])
