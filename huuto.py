#!/usr/bin/python3
# coding=utf-8

import configparser
import datetime
from dateutil import parser
import json
from pprint import pprint
import re
import requests
import time


###################################################
# Global vars
###################################################
huuto_api_url = 'https://api.huuto.net/1.1'
config_file = 'huuto_config.ini'


###################################################
# Define some exceptions
###################################################
class ApiError(Exception):
    pass


class ApiUnauthorizedError(ApiError):
    pass


class ApiForbiddenError(ApiError):
    pass


class ApiNotFoundError(ApiError):
    pass


class ApiBadRequestError(ApiError):
    pass


class ApiNotImplementedError(ApiError):
    pass


###################################################
# Helper functions
###################################################
def config():
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    return cfg['Huuto.net']


def token():
    """Returns auth token from config file"""
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    return cfg['token']['token']


def userid():
    """Returns userid from config file"""
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    return cfg['token']['userid']


def get_token_data():
    """Reads token details from config file."""
    cfg = configparser.ConfigParser()
    cfg.read(config_file)

    return cfg['token']


def update_token(token, start_time, expires, userid):
    """Write token, it's creation time, expiry time and the user's id to the config file"""
    cfg = configparser.ConfigParser()
    cfg.read(config_file)
    cfg['token'] = {
                    'userid': userid,
                    'token': token,
                    'start_time': start_time,
                    'expires': expires
    }
    with open(config_file, 'w') as configfile:
        cfg.write(configfile)


def _url(path):
    """
    Helper function to combine the passed api path with the api url

    Args:
        path (string) - relative path of the api endpoint

    Returns:
        (string) - The full url to the api endpoint
    """
    global huuto_api_url

    return huuto_api_url + path


def get(path, parameters=False, auth=False, accepted_status_codes=False):
    """
    Make a GET request against the api.

    Args:
        path (string) - Relative path to the api endpoint
        parameters (dict) - A dict with the key/value that will be formatted to URL parameters by requests.get()
        auth (boolean) - If the request should use the authentication token
        accepted_status_codes (list) - A list of http return codes that are ok for this query

    Returns:
        (dict) - The full json content of the response
    """
    # Avoiding the "mutable dict/list funtion argument" issue by not defining the default in the function def
    if not parameters:
        parameters = {}

    if not accepted_status_codes:
        accepted_status_codes = [200]

    if auth:
        authenticate()
        headers = {'X-HuutoApiToken': token()}
    else:
        headers = {}

    resp = requests.get(
        _url(path),
        params=parameters,
        headers=headers
    )
    validate_response(resp, accepted_status_codes)
    contents = json.loads(resp.content.decode('utf-8'))

    return contents


def post(path, data, auth=False, accepted_status_codes=False, files=None, data_as_json=False):
    """
    Make a POST request against the api.

    Args:
        path (string) - Relative path to the api endpoint
        data (dict) - A dict with the key/value parameters to be put into the data payload of the POST request
        auth (boolean) - If the request should use the authentication token
        accepted_status_codes (list) - A list of http return codes that are ok for this query
        files (dict) - Files to upload with the POST request. E.g. {'file': open('PATH_TO_FILE', 'rb')}
        data_as_json (boolean) - Some requests need the payload to be POSTed as 'json' (when they contain arrays),
            while some endpoint will only accept 'data' (e.g. authentication)

    Returns:
        (dict) - The full json content of the response
    """
    if auth:
        authenticate()
        headers = {'X-HuutoApiToken': token()}
    else:
        headers = {}

    # Avoiding the "mutable dict/list function argument" issue by not defining the default in the function def
    if not accepted_status_codes:
        accepted_status_codes = [200]

    if data_as_json:
        resp = requests.post(
            _url(path),
            json=data,
            headers=headers,
            files=files
        )
    else:
        resp = requests.post(
            _url(path),
            data=data,
            headers=headers,
            files=files
        )

    validate_response(resp, accepted_status_codes)
    #pprint(resp.request.headers)
    #pprint(resp.request.body)
    contents = json.loads(resp.content.decode('utf-8'))

    return contents


def put(path, data, auth=False, accepted_status_codes=False):
    """
    Make a PUT request against the api.

    Args:
        path (string) - Relative path to the api endpoint
        data (dict) - A dict with the key/value parameters to be put into the data payload of the PUT request
        auth (boolean) - If the request should use the authentication token
        accepted_status_codes (list) - A list of http return codes that are ok for this query

    Returns:
        (dict) - The full json content of the response
    """
    if auth:
        authenticate()
        headers = {'X-HuutoApiToken': token()}
    else:
        headers = {}

    # Avoiding the "mutable dict/list funtion argument" issue by not defining the default in the function def
    if not accepted_status_codes:
        accepted_status_codes = [200]

    resp = requests.put(
        _url(path),
        data=data,
        headers=headers
    )
    validate_response(resp, accepted_status_codes)
    contents = json.loads(resp.content.decode('utf-8'))

    return contents


def delete(path, auth=False, accepted_status_codes=False):
    """
    Make a DELETE request against the api.

    Args:
        path (string) - Relative path to the api endpoint
        auth (boolean) - If the request should use the authentication token
        accepted_status_codes (list) - A list of http return codes that are ok for this query

    Returns:
        (dict) - The full json content of the response
    """
    if auth:
        authenticate()
        headers = {'X-HuutoApiToken': token()}
    else:
        headers = {}

    # Avoiding the "mutable dict/list funtion argument" issue by not defining the default in the function def
    if not accepted_status_codes:
        accepted_status_codes = [200]

    resp = requests.delete(
        _url(path),
        headers=headers
    )
    validate_response(resp, accepted_status_codes)

    # Returning the full response object, because content is empty
    return resp


def validate_response(resp, accepted_status_codes):
    """
    Evaluate the return code of an api call and raise custom exceptions.
    You can pass multiple return codes, because some endpoints might return e.g.
    201 or other expected codes other than 200

    Args:
        resp (Response object) - The returned object of a 'requests.get()' that needs to be evaluated
        accepted_status_codes (list) - A list of http return codes that are ok for this query

    Raises:
        ApiBadRequestError: when form parameters are missing or invalid username/password
        ApiUnauthorizedError: When accessing an endpoint without (valid) token
        ApiForbiddenError: When accessing an endpoint without (valid) token
        ApiNotImplementedError: When querying an endpoint in an unsupported method, e.g. POST instead of GET
        ApiError: On any http return code that is not in the 'accepted_status_codes' parameter
    """
    if resp.status_code not in accepted_status_codes:
        pprint(resp.request.url)
        pprint(resp.request.headers)
        pprint(resp.request.body)
        pprint(resp.content)

    if resp.status_code == 400:
        raise ApiBadRequestError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))
    if resp.status_code == 401:
        raise ApiUnauthorizedError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))
    if resp.status_code == 403:
        raise ApiForbiddenError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))
    if resp.status_code == 404:
        raise ApiNotFoundError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))
    if resp.status_code == 501:
        raise ApiNotImplementedError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))
    if resp.status_code not in accepted_status_codes:
        raise ApiError('{} {} {}'.format(resp.request.method, resp.request.path_url, resp.status_code))


def is_type(var_name, variable, object_type):
    """
    Validates that the provided variable is of the expected type.

    Args:
        var_name (string) - name of the variable (for the exception message)
        variable (object) - the variable to be checked
        object_type (object type) - the expected type, e.g. 'int' or 'float'

    Returns:
        True - if variable value is 'None'
        True - if variable is of expected type. Raises a TypeError exception if not.
    """
    if variable is None:
        return True

    if not isinstance(variable, object_type):
        raise TypeError(
            'Expected value of type {} for "{}", but received "{}" instead.'.format(object_type, var_name, variable))
    else:
        return True


###################################################
# Root
###################################################
def get_endpoints():
    """List all methods and their api endpoints"""
    return get('/')


###################################################
# Authentication
###################################################
def authenticate():
    """
    Authenticate, get the token and store it in the global 'token' variable

    Method call returns a token id, which can be sent as the X-HuutoApiToken header field. Also token expiration time
    is returned as part of the data.
    Userid is the same userid used for Huuto.net. If you do not already have an account, you can register one through
    the main site (http://www.huuto.net).

    Status Codes:
        400 Bad Request - when form parameters are missing or invalid username/password
        201 Created - authentication token created
    """
    username = config()['username']
    password = config()['password']

    path = '/authentication'
    data = {
        'username': username,
        'password': password
    }

    token_data = get_token_data()
    token_expires = parser.parse(token_data['expires'])
    now = datetime.datetime.now(datetime.timezone.utc)

    print("Current token expires: ", token_data['expires'])

    if token_expires < now:
        print("Token expired, getting new one.")
        response = post(path, data, False, [200, 201])

        # Parsing the userid from the link in the auth response
        # Assuming that the userid is a number between 3-8 digits.
        match = re.search('/([0-9]{3,8})', response['links']['user'])
        matched_userid = match.group(1)

        update_token(
            response['authentication']['token']['id'],
            response['authentication']['token']['startTime'],
            response['authentication']['token']['expires'],
            matched_userid
        )

    return token()


###################################################
# Bids
###################################################
def get_item_bids(itemid):
    """
    Retrieve bids on an item.

    Args:
        itemid (int) - item's id
    """
    path = '/items/{}/bids'.format(itemid)

    return get(path)


def create_item_bid(itemid, bid, automate=0, quantity_min=1, quantity_max=1):
    """
    Place a bid on an item

    Args:
        itemid (int) - item's id
        bid (float) - bid amount (euros), eg. "16.50"
        automate (int (0 = no, 1 = yes). Default 0.) - Bidding automation. With automate on, bid parameter is considered
            to be the maximum amount the user is willing to pay. Bidding automation system will take care of the bidding
            process on behalf of the user and try to win the item with the smallest possible price.
        quantity_min (int) - Minimum quantity user is bidding for. Applies to items which have a quantity of more
            than one (eg. one is selling 10 USB sticks). Required if item has a quantity of more than one.
            Currently only buy-now items can have a quantity of more than one.
        quantity_max (int) - Maximum quantity user is bidding for. Required if item has a quantity of more than one.
            (See more info above.)
    """
    # This needs to be float
    bid = float(bid) if bid else None

    path = '/items/{}/bids'.format(itemid)
    data = {
        'itemid': itemid,
        'bid': bid,
        'automate': automate,
        'quantityMin': quantity_min,
        'quantityMax': quantity_max
    }

    return post(path, data, auth=True, accepted_status_codes=[200, 201])


###################################################
# Categories
###################################################
def get_categories(max_depth=3):
    """
    Retrieve category listing. Huuto has a 3-level category system.

    Args:
        max-depth (int (1, 2, 3)) - multiple hierarchy levels can be fetched in a single call
    """
    path = '/categories'
    params = {'max-depth': max_depth}

    return get(path, params)


def get_sub_categories(categoryid):
    """
    Retrieve subcategories of a specific category.

    Args:
        categoryid (int) - Category id
    """
    path = '/categories/{}/subcategories'.format(categoryid)

    return get(path)


def get_category_info(categoryid):
    """
    Retrieve information regarding a single category.

    Args:
        categoryid (int) - Category id
    """
    path = '/categories/{}'.format(categoryid)

    return get(path)


def get_category_items(categoryid, page=1):
    """
    Retrieve category items.
    Args:
        categoryid (int) - Category id
        page (int) - page
    """
    path = '/categories/{}/items'.format(categoryid)
    params = {'page': page}

    return get(path, params)


###################################################
# Items
###################################################
def create_item(buy_now_price=None, category_id=None, closing_time=None, condition=None, delivery_methods=None,
                delivery_terms=None, description=None, identification_required=None, is_location_abroad=None,
                list_time=None, marginal_tax=None, minimum_feedback=None, minimum_increase=None, open_days=None,
                original_id=None, payment_methods=None, payment_terms=None, postal_code=None, quantity=1,
                republish=None, sale_method=None, starting_price=None, status='preview', title=None, vat=None,
                offers_allowed=None
                ):
    """
    Create a new item.

    Note: Parameters with "None" value are omitted from the API call.

    Args:
        buy_now_price (float) - Buy now price. Required when sale method is "buy-now".
        category_id (int) - Item's category id
        closing_time (string - eg. '2016-12-04 18:55:20') - together with listTime, alternative to openDays
        condition (new - uusi, like-new - uudenveroinen, good - hyvä, acceptable - tyydyttävä, weak - heikko) -
            item's condition
        description (string) - item's description
        delivery_methods (list - pickup, shipment. Note: list!) - delivery methods
            ATTENTION - This can currently not be set through the API. Result is always empty!
        delivery_terms (string) - delivery terms
        identification_required (int - 0 or 1, boolean) - Require identification from buyers (optional, default 0).
            Option available for Huuto Plus users.
        is_location_abroad (int - 0 or 1, boolean) - If item is located outside of Finland or not.
            Default 0 (no). If set to 1, postalCode does not need to be used.
        list_time (string - eg. '2016-11-20 19:26:00') - together with closingTime,
            alternative to openDays (optional, defaults to current time)
        marginal_tax (int - 0 or 1, boolean) - Is marginal tax used or not. Available for company users.
        minimum_feedback (int) - minimum user feedback points required for buying/bidding
            (ostajien rajaaminen palautepistemäärän perusteella).
            Option available for Huuto Plus users.
        minimum_increase (float) - Minimum increase for bidding. (Not available for regular users.
            Required for Huuto Plus users, who can set this value freely.) Used only when sale method is "auction".
        open_days (int) - amount of days item will be available for selling
        original_id (int) - originalId can be used to easily republish an old, closed item.
            Title, description, sell method, price, images and other data will get copied from the previous into newly
            created item, which will have a "draft" status by default. To publish it, its status must be updated to
            "preview" and after that, to "published".
        payment_methods (list - wire-transfer, cash, mobile-pay. Multiple options can be sent. Note: list!)
        payment_terms (string - payment terms description, max. 1000 chars)
        postal_code (string - eg. '00100') - Finnish postal code. Mandatory field by default.
            However, if isLocationAbroad parameter is set to 1, postalCode is not required.
        quantity (int) - Quantity available for selling. Mandatory for buy-now items, where minimum is 1.
            Optional for auction items (set to 1 automatically).
        republish (int - 0 or 1, boolean) - Republish item (optional).
            If not sold, item will be republished automatically.
            Can be used for items that are open more than 3 days. Option is available only for Huuto Plus users.
        sale_method (string - auction, buy-now. Note: "Hybrid" method is no longer available.) - item's selling method
        starting_price (float) - Starting price for bidding. Required when sale method is "auction".
        status (string - draft, preview, published, closed, disabled, waiting) - item's status -
            When creating a new item, status will be "preview" by default.
        title (string - max. 60 chars) - Item's title
        vat (int - between 0-100) - Used vat rate as a percentage. Available for companies.
        offers_allowed (int - 0 or 1, boolean) - Allow offers from users. Allowed by default.

    More info about STATUS:
        To publish an item, you have to update your item's status to "published" via a PUT request.
        Item can not becreated directly into published state.
        Item can be created with draft status in which case no additional parameters are required.
        This is useful if an application wants to save item images before asking other parameters from user.
    """

    ##
    # Since there are many parameters and dependencies, let's do some validations before submitting the request
    # to the API. It might help catching certain issues early.

    # These need to be float
    buy_now_price = float(buy_now_price) if buy_now_price else None
    minimum_increase = float(minimum_increase) if minimum_increase else None
    starting_price = float(starting_price) if starting_price else None

    # Check type of input parameters
    is_type("category_id", category_id, int)
    is_type("delivery_methods", delivery_methods, list)
    is_type("minimum_feedback", minimum_feedback, int)
    is_type("open_days", open_days, int)
    is_type("original_id", original_id, int)
    is_type("payment_methods", payment_methods, list)
    is_type("quantity", quantity, int)

    # Various other validations

    # condition
    accepted_conditions = ['new', 'like-new', 'good', 'acceptable', 'weak']
    if condition and condition not in accepted_conditions:
        raise ValueError('"condition" must be one of these values: {}'.format(accepted_conditions))

    # closing_time must be formatted like: 2016-11-20 19:26:00
    if closing_time:
        try:
            time.strptime(closing_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return False

    if delivery_methods:
        for delivery_method in delivery_methods:
            if delivery_method not in ['pickup', 'shipment']:
                raise ValueError('delivery_methods must be "pickup" or "shipment".')

    # identification_required
    if identification_required and identification_required not in [0, 1]:
        raise ValueError('"identification_required" must be "0" or "1"')

    # is_location_abroad
    if is_location_abroad is not None and is_location_abroad not in [0, 1]:
        raise ValueError('"is_location_abroad" must be "0" or "1"')

    if is_location_abroad is not None and is_location_abroad == 0 and postal_code is None:
        raise ValueError('"postal_code" can not be empty if "is_location_abroad=0"')

    # list_time must be formatted like: 2016-11-20 19:26:00
    if list_time:
        try:
            time.strptime(list_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return False

    # list_time and closing_time
    # XOR check, need to have both or none set
    if bool(list_time) != bool(closing_time):
        raise ValueError('Must set both "list_time" and "closing_time".')

    if not bool(list_time) != bool(open_days):
        raise ValueError('Must set either "list_time/closing_time" or "open_days".')

    # marginal_tax
    if marginal_tax and marginal_tax not in [0, 1]:
        raise ValueError('"marginal_tax" must be "0" or "1"')

    # minimum_increase
    if minimum_increase and minimum_increase not in [0, 1]:
        raise ValueError('"minimum_increase" must be "0" or "1"')

    # offers_allowed
    if offers_allowed and offers_allowed not in [0, 1]:
        raise ValueError('"offers_allowed" must be "0" or "1"')

    # payment_methods
    if payment_methods:
        for payment_method in payment_methods:
            if payment_method not in ['wire-transfer', 'cash', 'mobile-pay']:
                raise ValueError('payment_methods must contain "wire-transfer", "cash" and/or "mobile-pay".')

    # quantity
    if not isinstance(quantity, int):
        raise TypeError('Expected int value for "quantity", but received "{}" instead.'.format(quantity))

    # republish
    if republish and republish not in [0, 1]:
        raise ValueError('"republish" must be "0" or "1"')

    # sale_method
    if sale_method not in ['auction', 'buy-now']:
        raise ValueError('sale_method must be "auction" or "buy-now".')

    if sale_method == 'buy-now' and buy_now_price is None:
        raise ValueError('Must set "buy_now_price" when using "sale_method=buy-now".')

    if sale_method == 'buy-now' and minimum_increase is not None:
        raise ValueError('Must set "minimum_increase" only available for "sale_method=auction".')

    if sale_method == 'auction' and starting_price is None:
        raise ValueError('Must set "starting_price" when using "sale_method=auction".')

    # status
    if status not in ['draft', 'preview']:
        raise ValueError('status must be "draft" or "preview".')

    # vat
    if vat and vat not in range(0, 100):
        raise ValueError('"vat" must be between 0 - 100')

    path = '/items'
    data = {
        'buyNowPrice': buy_now_price,
        'categoryId': category_id,
        'closingTime': closing_time,
        'condition': condition,
        'deliveryMethods ': delivery_methods,
        'deliveryTerms': delivery_terms,
        'description': description,
        'identificationRequired': identification_required,
        'isLocationAbroad': is_location_abroad,
        'listTime': list_time,
        'marginalTax': marginal_tax,
        'minimumFeedback': minimum_feedback,
        'minimumIncrease': minimum_increase,
        'offersAllowed': offers_allowed,
        'openDays': open_days,
        'originalId': original_id,
        'paymentMethods': payment_methods,
        'paymentTerms': payment_terms,
        'postalCode': postal_code,
        'quantity': quantity,
        'republish': republish,
        'saleMethod': sale_method,
        'startingPrice': starting_price,
        'status': status,
        'title': title,
        'vat': vat
    }

    # Drop all elements where the value is "None"
    data = {k: v for k, v in data.items() if v is not None}

    return post(path, data, auth=True, accepted_status_codes=[200, 201], data_as_json=True)


def edit_item(item_id,
              buy_now_price=None, category_id=None, closing_time=None, condition=None, delivery_methods=None,
              delivery_terms=None, description=None, identification_required=None, is_location_abroad=None,
              list_time=None, marginal_tax=None, minimum_feedback=None, minimum_increase=None, open_days=None,
              original_id=None, payment_methods=None, payment_terms=None, postal_code=None, quantity=None,
              republish=None, sale_method=None, starting_price=None, status='preview', title=None, vat=None,
              offers_allowed=None
              ):
    """
    Editing items

    Note that items can be edited only in preview or draft state.

    Attention:
        Items created in preview status, can not be seen in the webui, but only queried
        from the api with get_item_own().

    Args:
        item_id (int): Id of the item to be edited, mandatory.

        Edit accepts the same parameters as create_item (see above for reference).
    """

    path = '/items/{}/'.format(item_id)
    data = {
        'buyNowPrice': buy_now_price,
        'categoryId': category_id,
        'closingTime': closing_time,
        'condition': condition,
        'deliveryMethods ': delivery_methods,
        'deliveryTerms': delivery_terms,
        'description': description,
        'identificationRequired': identification_required,
        'isLocationAbroad': is_location_abroad,
        'listTime': list_time,
        'marginalTax': marginal_tax,
        'minimum_feedback': minimum_feedback,
        'minimum_increase': minimum_increase,
        'offersAllowed': offers_allowed,
        'openDays': open_days,
        'originalId': original_id,
        'paymentMethods': payment_methods,
        'paymentTerms': payment_terms,
        'postalCode': postal_code,
        'quantity': quantity,
        'republish': republish,
        'saleMethod': sale_method,
        'starting_price': starting_price,
        'status': status,
        'title': title,
        'vat': vat
    }

    # Drop all elements where the value is "None"
    data = {k: v for k, v in data.items() if v is not None}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])#, data_as_json=True)


def preview_item(item_id):
    """
    Set item's status to "preview".
    At this point all saved data will be validated.
    After a successful "preview", an item can published.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)
    data = {'status': 'preview'}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])


def publish_item(item_id):
    """
    Publish an item and make it available for selling.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)
    data = {'status': 'published'}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])


def close_item(item_id):
    """
    Close item.

    After closing item is no longer available for bidding, offering etc.
    Highest bidder will win, if other conditions (eg. price reservation) are met.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)
    data = {'status': 'closed'}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])


def get_item(item_id):
    """
    Retrieve item's data.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)

    return get(path)


def get_item_own(item_id):
    """
    Retrieve your own item's data. Requires authentication.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)

    return get(path, auth=True)


def delete_item(item_id):
    """
    Items in draft status can be deleted via DELETE requests.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
    """
    path = '/items/{}/'.format(item_id)

    return delete(path, auth=True, accepted_status_codes=[204])


def list_items(addtime=None, area=None, biddernro=None, category=None, classification=None, closingtime=None,
               feedback_limit=None, limit=None, page=None, price_max=None, price_min=None, seller_type=None,
               sellernro=None, sellstyle=None, sort=None, status=None, words=None
               ):
    """
    Item search. Various parameters can be used.

    Args:
        addtime (string - past-day, past-2days, past-5days, past-week) - item's list time
        area (string - eg. "Helsinki", "Uusimaa", "00100") - city, municipality or zipcode
        biddernro (int) - bidder's numeric user id
        category (int | string) - category's id, multiple category id's can be separated with commas or dashes, 
            eg. 1-2-3
        classification (string - none - ei määritelty, new - uusi, like-new - uudenveroinen, good - hyvä,
            acceptable - tyydyttävä, weak - heikko) - item's condition. In the API documentation this parameter is
            called condition, but judging by the API response, classification is the actual parameter name.
        closingtime (string - next-day, next-2days, next-5days, next-week) - item's list time
        feedback_limit (int) - filter by user's feedback value
        limit (int (50 | 500) - default is 50) - items per page limit
        page (int) - result set page number
        price_max (float) - maximum price
        price_min (float) - minimum price
        seller_type (string - company, user) - seller's type, default is all.
        sellernro (int) - seller's numeric user id
        sellstyle (string - all, auction, buy-now) - item's selling method
        sort (string - hits, newest, closing, lowprice, highprice, bidders, title.
            Default is "hits".) - result rest sorting
        status (string - open, closed) - item's status
        words (string) - search string
    """

    # We need to do some validation here, because when using a search parameter with predefined values,
    # like "addtime", any misspelling will be gracefully ignored by the API and the parameter will be
    # ignored completely (and without feedback). Only indicator that a parameter was ignored is that
    # in the response the parameters in the "links/self" link doesn't match the input parameters.

    if addtime and addtime not in ['past-day', 'past-2days', 'past-5days', 'past-week']:
        raise ValueError('addtime must be one of these values: "past-day", "past-2days", "past-5days", "past-week"')

    if classification and classification not in ['none', 'new', 'like-new', 'good', 'acceptable', 'weak']:
        raise ValueError('classification must be one of these values: "none", "new", "like-new", "good", "acceptable", "weak"')

    if limit and limit not in [50, 500]:
        raise ValueError('"limit" must be either 50 or 500')

    if sellstyle and sellstyle not in ['all', 'auction', 'buy-now']:
        raise ValueError('sellstyle must be one of these values: "all", "auction", "buy-now"')

    if sort and sort not in ['hits', 'newest', 'closing', 'lowprice', 'highprice', 'bidders', 'title']:
        raise ValueError('sort must be one of these values: '
                         'hits, newest, closing, lowprice, highprice, bidders, title')

    is_type("biddernro", biddernro, int)
    is_type("feedback_limit", feedback_limit, int)
    is_type("page", page, int)
    is_type("sellernro", sellernro, int)

    # These need to be float
    price_min = float(price_min) if price_min else None
    price_max = float(price_max) if price_max else None

    path = '/items'
    params = {'addtime': addtime,
              'area': area,
              'biddernro': biddernro,
              'category': category,
              'classification': classification,
              'closingtime': closingtime,
              'feedback_limit': feedback_limit,
              'limit': limit,
              'page': page,
              'price_min': price_min,
              'price_max': price_max,
              'seller_type': seller_type,
              'sellernro': sellernro,
              'sellstyle': sellstyle,
              'sort': sort,
              'status': status,
              'words': words
              }

    return get(path, params)


###################################################
# Images
###################################################
def get_item_images(itemid):
    """
    Retrieve images related to item.

    Args:
        itemid (int) - item's id
    """
    path = '/items/{}/images'.format(itemid)

    return get(path)


def add_item_image(itemid, image):
    """
    Post an image to item.

    Item must exist before images can be added.
    Item must be in preview or draft state.
    Creating an item with draft status is useful if the application wants to save item images before asking
    any other parameters from the user. When request status is draft, no additional parameters are required.

    Args:
        itemid (int) - item's id (already present in the url)
        image (file) - local path to image file
    """
    path = '/items/{}/images'.format(itemid)
    data = {}
    files = {'file': open(image, 'rb')}

    return post(path, data, auth=True, files=files)


def delete_item_image(itemid, imageid):
    """
    Delete an image from item.

    Args:
        itemid (int) - item's id
        imageid (int) - image's id

    Status Codes:
        204 No Content – when image deleted successfully
    """
    path = '/items/{}/images/{}'.format(itemid, imageid)

    return delete(path, auth=True, accepted_status_codes=[204])


###################################################
# Offers
###################################################
def get_item_offers(itemid):
    """
    Retrieve information about item's offers

    Args:
        itemid (int) - item's id
    """
    path = '/items/{}/offers'.format(itemid)

    return get(path)


def create_item_offer(itemid, offer, message):
    """
    Post a new offer (hintaehdotus) to item.

    Args:
        itemid (int) - item's id
        offer (float) - offer amount (euros), eg. "16.50"
        message (string(255)) - message related to offer
    """
    path = '/items/{}/offers'.format(itemid)
    data = {'offer': offer, 'message': message}

    return post(path, data, auth=True, accepted_status_codes=[200, 201])


def answer_item_offer(itemid, offerid, status):
    """
    Seller can accept or refuse offers made by users.
    Users can cancel offers made by themselves.
    Cancelling can only be done if seller has not yet accepted or refused the offer in question.

    Args:
        itemid (int) - item's id
        offerid (int) - offer's id
        status (string) - offer status to be updated
    """
    # TODO: find out what different offer statuses are available

    path = '/items/{}/offer/{}'.format(itemid, offerid)
    data = {'status': status}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])


###################################################
# Questions
###################################################
def get_item_questions(itemid):
    """
    Retrieve information about item's questions and seller's answers.

    Args:
        itemid (int) - item's id
    """
    path = '/items/{}/questions'.format(itemid)

    return get(path)


def create_item_question(itemid, question):
    """
    Post a new offer (hintaehdotus) to item.

    Args:
        itemid (int) - item's id
        question (string(255)) – question text
    """
    path = '/items/{}/offers'.format(itemid)
    data = {'question': question}

    return post(path, data, auth=True, accepted_status_codes=[200, 201])


def answer_item_question(itemid, questionid, answer):
    """
    Answer to a question. Only seller can post answers.

    Args:
        itemid (int) - item's id
        questionid (int) - item's id
        answer (string(255)) - answer text
    """
    path = '/items/{}/question/{}'.format(itemid, questionid)
    data = {'answer': answer}

    return put(path, data, auth=True, accepted_status_codes=[200, 201])


###################################################
# Users
###################################################
def get_user_info():
    """
    Retrieve user information.

    Note: LastLogin is only visible for the user herself.
    Address is only visible for the user herself and for users who have sold items to the user or have bought items from
     the user.
    """
    path = '/users/{}/'.format(userid())

    return get(path, auth=True)


def get_user_settings():
    """
    Retrieve user-specific parameter requirements for creating item, e.g. which parameters are allowed or required and
    what values are allowed for a certain parameter.

    Status Codes:
        403 Forbidden - when token is not used or it is invalid
    """
    path = '/users/{}/settings'.format(userid())

    return get(path, auth=True)


def get_user_feedbacks():
    """Retrieve user feedbacks."""
    path = '/users/{}/feedbacks'.format(userid())

    return get(path, auth=True)


def get_user_favorites():
    """Retrieve user's favorite items. Also known as "Muistilista"."""
    path = '/users/{}/favorites'.format(userid())

    return get(path, auth=True)


#    ATTENTION: There is no documented DELETE method to remove favorites!
#    Note for posterity: Through the web interface, favorites are removed with:
#    POST https://www.huuto.net/item-favorite/poista/itemid/450185678
#    And auth token in the headers.


def add_user_favorites(itemid):
    """
    Add item to user's favorite list.

    Args:
        itemid (int) – item id

    Status Codes:
        201 Created – when favorite successfully created
    """
    path = '/users/{}/favorites'.format(userid())
    data = {'itemid': itemid}

    return post(path, data, auth=True, accepted_status_codes=[201])


# WARNING: http://dev.huuto.net/methods.html#user-purchases wrongly documents this as a POST, when it should be GET
# Also "post_id" from the documentation doesn't seem to do anything.
def get_user_purchases(status='all', post_id=False):
    """
    Retrieve items which user has bidded or purchased.

    Args:
        post_id (int) - post's unique id <<< DOESN'T SEEM TO DO ANYTHING!!!
        status (string) - item's status - options: open, closed, processing, all

    """
    path = '/users/{}/purchases'.format(userid())
    params = {'status': status, 'post_id': post_id}

    return get(path, params, auth=True)


def get_user_sales(page=1, status='all', sold=0, sort='closing-time', republished=''):
    """
    Retrieve items created by user.

    Args:
        republished (int - set eg. to 1 to enable filter) - If item is republished or not.
            Effective only if status "open" or "closed" is used at the same time.
        sold (int (0 or 1)) - If item is sold or not.
            Effective only if status "open" or "closed" is used at the same time.
        status (string - all, open, closed, waiting, draft) - item status
        sort (string - bidders, closing-time, current-price, list-time) - result set sorting
        page (int) - result page number
    """
    path = '/users/{}/sales'.format(userid())
    data = {
        'page': page,
        'status': status,
        'sold': sold,
        'sort': sort,
        'republished': republished
    }

    return get(path, data, auth=True)
