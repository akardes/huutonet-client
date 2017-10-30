###
# huuto_test_public.py
#
# Tests publicly available api methods
#
# Run with: nosetests3 huuto_test_public.py
#

import huuto
import huuto_test_helpers
from nose.tools import assert_true
from nose.tools import assert_equal
from nose.tools import assert_raises


###################################################
# Tests
###################################################
def test_get_endpoints_response():
    response = huuto.get_endpoints()

    assert_true(isinstance(response, dict))


def test_get_item_bids_response_ok():
    item_id = huuto_test_helpers.get_random_item_id()
    response = huuto.get_item_bids(item_id)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['bids'], list))
    assert_true(response['links']['self'].find(str(item_id)) > -1)


def test_get_item_bids_response_fail():
    item_id = 123456

    assert_raises(huuto.ApiNotFoundError, huuto.get_item_bids, item_id)


def test_get_categories_response_ok():
    response = huuto.get_categories()

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['categories'][0]['links']['items'], str))


def test_get_sub_categories_response_ok():
    response = huuto.get_sub_categories(1)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['categories'][0]['links']['items'], str))


def test_get_sub_categories_response_fail():
    response = huuto.get_sub_categories(999999)

    assert_true(isinstance(response, dict))
    assert_equal(response['id'], None)


def test_get_category_info_response_ok():
    response = huuto.get_category_info(1)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['title'], str))


def test_get_category_info_response_fail():
    response = huuto.get_category_info(999999)

    assert_true(isinstance(response, dict))
    assert_equal(response['id'], None)


def test_get_category_items_response_ok():
    response = huuto.get_category_items(1)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['items'][0]['id'], int))


def test_get_category_items_response_fail():
    """
    API returns items even if the passed category doesn't exist.
    Therefore comparing if one of the returned item's category links has the same category id.
    """
    category_id = 999999
    response = huuto.get_category_items(category_id)

    assert_true(isinstance(response, dict))
    assert_true(response['items'][0]['links']['category'].find(str(category_id)) == -1)


def test_get_item_response_ok():
    item_id = huuto_test_helpers.get_random_item_id()
    response = huuto.get_item(item_id)

    assert_true(isinstance(response, dict))
    assert_equal(response['id'], item_id)


def test_get_item_response_fail():
    item_id = 999999

    assert_raises(huuto.ApiNotFoundError, huuto.get_item, item_id)


def test_list_items_response_ok():
    """
    In order to test that the search results have been passed as expected to the API,
    we test that our search parameters are in the 'self' link that we get back with the request.
    """
    params = {
        "addtime": "past-5days",
        "classification": "new",
        "feedback_limit": 1,
        "limit": 500,
        "page": 2,
        "price_min": 1,
        "price_max": 10,
        "words": "levy"
    }

    response = huuto.list_items(**params)

    link_self = response['links']['self']

    assert_true(isinstance(response, dict))

    for k, v in params.items():
        assert_true(
            link_self.find("{}={}".format(k, v)) > -1,
            "{} parameter doesn't match with API response: {}".format(k, link_self)
        )


def test_list_items_response_fail():
    """
    In order to test that the search results have been passed as expected to the API,
    we test that our search parameters are in the 'self' link that we get back with the request.
    """
    params = {
        "addtime": "past-99days",
        "classification": "foo",
        "limit": 501,
        "sellstyle": "foo",
        "sort": "foo"
    }

    for k, v in params.items():
        assert_raises(ValueError, huuto.list_items, {k: v})


def test_get_item_images_response_ok():
    item_id = huuto_test_helpers.get_random_item_id()
    response = huuto.get_item_images(item_id)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['images'][0]['links'], dict))


def test_get_item_images_response_fail():
    item_id = 999999

    assert_raises(huuto.ApiNotFoundError, huuto.get_item_images, item_id)


def test_get_item_offers_response_ok():
    item_id = huuto_test_helpers.get_random_item_id()
    response = huuto.get_item_offers(item_id)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['offers'], list))
    assert_true(response['links']['self'].find(str(item_id)) > -1)


def test_get_item_offers_response_fail():
    item_id = 999999

    assert_raises(huuto.ApiNotFoundError, huuto.get_item_offers, item_id)


def test_get_item_questions_response_ok():
    item_id = huuto_test_helpers.get_random_item_id()
    response = huuto.get_item_questions(item_id)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['questions'], list))
    assert_true(response['links']['self'].find(str(item_id)) > -1)


def test_get_item_questions_response_fail():
    item_id = 999999

    assert_raises(huuto.ApiNotFoundError, huuto.get_item_questions, item_id)
