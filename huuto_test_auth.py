###
# huuto_test_auth.py
#
# Tests api methods that require authentication
# Requires a huuto.net account and will create, edit and delete items, without publishing them.
#
# Not testing features for HuutoPlus users.
#
# Run with: nosetests3 huuto_test_auth.py
#

from datetime import datetime, timedelta
import huuto
import huuto_test_helpers
from nose.tools import assert_true
from nose.tools import assert_raises
from pprint import pprint
import requests


###################################################
# Global vars
###################################################

# Subcategory 527: Sekalaista
category_id = 527


###################################################
# Tests
###################################################
def test_auth_token():
    token = huuto.authenticate()

    assert_true(isinstance(token, str), pprint(token))
    assert_true(len(token) == 32, pprint(token))


def test_create_item_auction():
    """
    Testing to create an auction item.
    This is an item with postal code.
    This item uses open_days instead of list_time and closing_time.
    """
    data = {
        'category_id': category_id,
        'condition': 'weak',
        'delivery_methods': ['pickup', 'shipment'],
        'delivery_terms': 'no terms',
        'description': 'This is just a test item. Do not bid!',
        'is_location_abroad': 0,
        'offers_allowed': 1,
        'open_days': 3,
        'payment_methods': ['cash', 'mobile-pay', 'wire-transfer'],
        'payment_terms': 'Pay asap',
        'postal_code': '02780',
        'quantity': 1,
        'sale_method': 'auction',
        'starting_price': 101.01,
        'title': 'A buy now test item from Espoo'
    }

    response = huuto.create_item(**data)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['id'], int))

    assert_true(response['condition'] == data['condition'], pprint(response))
    assert_true(response['deliveryTerms'] == data['delivery_terms'], pprint(response))
    assert_true(response['location'] == 'ESPOO', pprint(response))
    assert_true(response['saleMethod'] == data['sale_method'], pprint(response))
    assert_true(response['startingPrice'] == data['starting_price'], pprint(response))
    assert_true(response['status'] == 'preview', pprint(response))
    assert_true(response['title'] == data['title'], pprint(response))
    assert_true(response['paymentTerms'] == data['payment_terms'], pprint(response))
    assert_true(response['postalCode'] == data['postal_code'], pprint(response))
    assert_true(response['quantity'] == data['quantity'], pprint(response))

    # There is a bug in the API that causes the deliveryMethods to be empty no matter what input
    # when it is fixed, the below line can be uncommented
    #assert_true(response['deliveryMethods'] == data['delivery_methods'], pprint(response))

    # When the test below fails, then it means Huuto.net has probably fixed the API and this assertion can be deleted
    assert_true(response['deliveryMethods'] == [], pprint(response))


def test_create_item_buynow():
    """
    Testing to create a buynow item.
    This is also an abroad item.
    This item uses list_time and closing_time instead of open_days
    """
    closing_time = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now() + timedelta(days=1))
    list_time = '{0:%Y-%m-%d %H:%M:%S}'.format(datetime.now() + timedelta(minutes=0))

    data = {
        'buy_now_price': 99.99,
        'category_id': category_id,
        'closing_time': closing_time,
        'condition': 'new',
        'delivery_methods': ['pickup', 'shipment'],
        'delivery_terms': 'no terms',
        'description': 'This is just a test item. Do not bid!',
        'is_location_abroad': 1,
        'list_time': list_time,
        'offers_allowed': 1,
        'payment_methods': ['cash', 'mobile-pay', 'wire-transfer'],
        'payment_terms': 'Pay asap',
        'quantity': 99,
        'sale_method': 'buy-now',
        'title': 'A buy now test item abroad'
    }

    response = huuto.create_item(**data)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['id'], int))

    assert_true(response['buyNowPrice'] == data['buy_now_price'], pprint(response))
    assert_true(response['condition'] == data['condition'], pprint(response))
    assert_true(response['deliveryTerms'] == data['delivery_terms'], pprint(response))
    assert_true(response['location'] == 'Ulkomaat', pprint(response))
    assert_true(response['saleMethod'] == data['sale_method'], pprint(response))
    assert_true(response['status'] == 'preview', pprint(response))
    assert_true(response['title'] == data['title'], pprint(response))
    assert_true(response['paymentTerms'] == data['payment_terms'], pprint(response))
    #assert_true(response['postalCode'] == data['postal_code'], pprint(response))
    assert_true(response['quantity'] == data['quantity'], pprint(response))

    # There is a bug in the API that causes the deliveryMethods to be empty no matter what input
    # when it is fixed, the below line can be uncommented
    #assert_true(response['deliveryMethods'] == data['delivery_methods'], pprint(response))

    # When the test below fails, then it means Huuto.net has probably fixed the API and this assertion can be deleted
    assert_true(response['deliveryMethods'] == [], pprint(response))


def test_create_item_draft():
    """
    Testing creating an item in draft status.
    Not much data to enter and test here.
    """
    data = {
        'status': 'draft',
        'open_days': 3,
        'sale_method': 'auction',
        'starting_price': 1
    }

    response = huuto.create_item(**data)

    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['id'], int))

    assert_true(response['status'] == 'draft', pprint(response))


def test_edit_item():
    pass


def test_preview_item():
    pass


def test_publish_item():
    pass


def test_close_item():
    pass


def test_delete_draft_item():
    # Create a draft item
    data = {
        'status': 'draft',
        'open_days': 3,
        'sale_method': 'auction',
        'starting_price': 1
    }

    response = huuto.create_item(**data)

    # Let's test that we actually created a draft item
    assert_true(isinstance(response, dict))
    assert_true(isinstance(response['id'], int))

    assert_true(response['status'] == 'draft', pprint(response))

    # Now delete it
    response = huuto.delete_item(response['id'])
    assert_true(response.status_code == 204, pprint(response))


def test_get_own_item():
    pass


def test_add_item_image():
    #    image = requests.get('http://lorempixel.com/640/400/abstract/test%20listing/')
    #    huuto.add_item_image(itemid, image.content)

    pass


def test_delete_item_images():
    pass


def test_create_item_offer():
    pass


def test_answer_item_offer():
    pass


def test_create_item_question():
    pass


def test_answer_item_question():
    pass


def test_get_user_info():
    pass


def test_get_user_settings():
    pass


def test_get_user_feedbacks():
    pass


def test_get_user_favourites():
    pass


def test_add_user_favourites():
    pass


def test_get_user_purchases():
    pass


def test_get_user_sales():
    pass


def test_create_item_bid():
    """
    Well this is a test that would be best to do against a mock interface
    unless you're willing to bid on something...
    """
    pass

