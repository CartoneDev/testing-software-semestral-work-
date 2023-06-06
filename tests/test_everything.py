import pytest
import util
from tests.Account import Account
from tests.Bucket import Bucket
from tests.Search import Search


@pytest.fixture(scope='session', autouse=True, name='driver')
def shared_data(request):
    driver = util.get_driver(request, "")
    yield driver
    driver.close()


@pytest.mark.run(order=1)
def test_login_from_main_page(driver):
    assert Account().test_login_from_main_page(driver)


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


def test_address_change_success_reported(driver):
    assert Account().test_address_change(driver)


def test_name_cant_change_contains_digits(driver):
    assert Account().test_name_change_contains_digits(driver)


def test_mail_is_mail_on_change(driver):
    assert Account().test_change_mail(driver)


@pytest.mark.parametrize("path_to_csv", ["data/personal_info.csv", "tests/data/personal_info.csv"])
def test_batched_account_info_change(driver, path_to_csv):
    csv_data = util.get_data_from_csv(path_to_csv, False)
    objects = util.parse_csv_to_objects(csv_data)
    for object in objects:
        assert Account().test_change_personal_info(driver, object)


@pytest.mark.parametrize("path_to_csv", ["data/shipping.csv", "tests/data/shipping.csv"])
def test_different_shipping_methods(driver, path_to_csv):
    csv_data = util.get_data_from_csv(path_to_csv, False)
    objects = util.parse_csv_to_objects(csv_data)
    for shipping in objects:
        if shipping["service"] != "zasilkovna":
            continue
        assert Bucket().test_different_shipping_methods(driver, shipping)
