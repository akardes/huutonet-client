# Huuto.net API Python Client 

This API client allows you to interact with the Huuto.net API in your Python projects.

**This client is still work in progress and not all of the methods have been tested, but I haven't had as much time to continue therefore publishing this already in hope that it will be useful for someone and get some contributions.**

## Getting Started

### Prerequisites

The client is written in and requires Python 3 and heavily uses the `requests` Python package. (Install with `pip3 install requests`)

Tests require `nosetests3`. (Install e.g. in Ubuntu `sudo apt install python3-nose`)

### Restrictions
Due to a bug in the Huuto.net API itself, it is currently not possible to set the "Delivery Method" property when creating an item through the API.
This API client still provides the options to set the Delivery Method and passes it to the API, but will currently just silently ignored by the Huuto.net API.
You can still use this client to create auctions or buy-now items, but Delivery Method will be unset. (August 2017)

### Setup

#### Public API access
For accessing the public API, you can copy `huuto.py` into your project and just import it with `import huuto`.

#### Authenticated access
Copy the file `huuto_config_template.ini` to the same directory as `huuto.py` and name it `huuto_config.ini`.
Enter you username and password.

## Documentation

### About this client
This client and all it's functions are implemented to be a 1:1 replication of the API documented in 
the [Huuto.net Developer Documentation](http://dev.huuto.net/index.html).

### Authentication
API calls that require authentication will use the credentials from the `huuto_config.ini` and after 
each successful login will safe the latest authentication token and it's expiry time in the same file. 
Subsequent authentications will reuse the cached token until it expires.  

### Usage example
```python
# Import this client and prettyprint so we can print nicely formatted responses from the API.
import huuto
from pprint import pprint

# List first page of items in category "127" (Hobbies)
items = huuto.get_category_items(127)
pprint (items)

# List second page of items
items = huuto.get_category_items(127, page=2)
pprint (items)

# Get the bids for item 448405493
bids = huuto.get_item_bids(448405493)
pprint(bids)

# Creating a buy-now item
data = {
    'buy_now_price': 99.99,
    'category_id': 127,
    'closing_time': '2017-01-08 12:00:00',
    'condition': 'new',
    'delivery_methods': ['pickup', 'shipment'],
    'delivery_terms': 'no terms',
    'description': 'This is just a test item. Do not bid!',
    'is_location_abroad': 1,
    'list_time': '2017-01-01 00:00:00',
    'offers_allowed': 1,
    'payment_methods': ['cash', 'mobile-pay', 'wire-transfer'],
    'payment_terms': 'Pay asap',
    'quantity': 99,
    'sale_method': 'buy-now',
    'title': 'A buy now test item abroad'
}
item = huuto.create_item(**data)
pprint(item)

```

### API Calls
#### get_item_bids(itemid)
Get bids for an item.

    Args:
        itemid (int) - item’s id
       

#### create_item_bid(itemid, bid, automate=0, quantity_min=1, quantity_max=1)
Place a bid on an item.

    Args:
        itemid (int) - item’s id
        bid (float) - bid amount (euros), eg. “16.50”
        automate (int (0 = no, 1 = yes). Default 0.) - Bidding automation. With automate on, bid parameter is considered
            to be the maximum amount the user is willing to pay. Bidding automation system will take care of the bidding
            process on behalf of the user and try to win the item with the smallest possible price.
        quantity_min (int) - Minimum quantity user is bidding for. Applies to items which have a quantity of more
            than one (eg. one is selling 10 USB sticks). Required if item has a quantity of more than one.
            Currently only buy-now items can have a quantity of more than one.
        quantity_max (int) - Maximum quantity user is bidding for. Required if item has a quantity of more than one.
            (See more info above.)


#### get_categories(max_depth=3)
Retrieve category listing. Huuto has a 3-level category system.

    Args:
        max-depth (int (1, 2, 3)) - multiple hierarchy levels can be fetched in a single call


#### get_sub_categories(categoryid)
Retrieve subcategories of a specific category.
    
    Args:
        categoryid (int) - Category id

#### get_category_info(categoryid)
Retrieve information regarding a single category.

    Args:
        categoryid (int) - Category id

#### get_category_items(categoryid, page=1)
Retrieve category items.
    Args:
        categoryid (int) - Category id
        page (int) - page


#### create_item(**args)
Create a new item.

Note: Parameters with "None" value are omitted from the API call.

    Args:
        buy_now_price (float) - Buy now price. Required when sale method is “buy-now”.
        category_id (int) - Item’s category id
        closing_time (string - eg. '2016-12-04 18:55:20') - together with listTime, alternative to openDays
        condition (new - uusi, like-new - uudenveroinen, good - hyvä, acceptable - tyydyttävä, weak - heikko) -
            item’s condition
        description (string) - item’s description
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
            Required for Huuto Plus users, who can set this value freely.) Used only when sale method is “auction”.
        open_days (int) - amount of days item will be available for selling
        original_id (int) - originalId can be used to easily republish an old, closed item.
            Title, description, sell method, price, images and other data will get copied from the previous into newly
            created item, which will have a “draft” status by default. To publish it, its status must be updated to
            “preview” and after that, to “published”.
        payment_methods (list - wire-transfer, cash, mobile-pay. Multiple options can be sent. Note: list!)
        payment_terms (string - payment terms description, max. 1000 chars)
        postal_code (string - eg. '00100') - Finnish postal code. Mandatory field by default.
            However, if isLocationAbroad parameter is set to 1, postalCode is not required.
        quantity (int) - Quantity available for selling. Mandatory for buy-now items, where minimum is 1.
            Optional for auction items (set to 1 automatically).
        republish (int - 0 or 1, boolean) - Republish item (optional).
            If not sold, item will be republished automatically.
            Can be used for items that are open more than 3 days. Option is available only for Huuto Plus users.
        sale_method (string - auction, buy-now. Note: “Hybrid” method is no longer available.) - item’s selling method
        starting_price (float) - Starting price for bidding. Required when sale method is “auction”.
        status (string - draft, preview, published, closed, disabled, waiting) - item’s status -
            When creating a new item, status will be “preview” by default.
        title (string - max. 60 chars) - Item’s title
        vat (int - between 0-100) - Used vat rate as a percentage. Available for companies.
        offers_allowed (int - 0 or 1, boolean) - Allow offers from users. Allowed by default.

More info about STATUS:

To publish an item, you have to update your item’s status to “published” via a PUT request.
Item can not becreated directly into published state.
Item can be created with draft status in which case no additional parameters are required.
This is useful if an application wants to save item images before asking other parameters from user.

#### edit_item(item_id, **args)
Editing items

Note that items can be edited only in preview or draft state.

Attention:
    Items created in preview status, can not be seen in the webui, but only queried
    from the api with get_item_own().

    Args:
        item_id (int): Id of the item to be edited, mandatory.

        Edit accepts the same parameters as create_item (see above for reference).

#### preview_item(item_id)
Set item’s status to “preview”.

At this point all saved data will be validated.

After a successful “preview”, an item can published.

    Args:
        item_id (int): Id of the item to be edited, mandatory.

#### publish_item(item_id)
Publish an item and make it available for selling.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
        
#### close_item(item_id)
Close item.

After closing item is no longer available for bidding, offering etc.
Highest bidder will win, if other conditions (eg. price reservation) are met.

    Args:
        item_id (int): Id of the item to be edited, mandatory.

#### get_item(item_id)
Retrieve item’s data.

    Args:
        item_id (int): Id of the item to be edited, mandatory.
      

#### get_item_own(item_id)
Retrieve your own item’s data. Requires authentication.

    Args:
        item_id (int): Id of the item to be edited, mandatory.


#### delete_item(item_id)
Items in **draft** status can be deleted via DELETE requests.

    Args:
        item_id (int): Id of the item to be edited, mandatory.

#### list_items(**args)
Item search. Various parameters can be used.

    Args:
        addtime (string - past-day, past-2days, past-5days, past-week) - item’s list time
        area (string - eg. "Helsinki", "Uusimaa", "00100") - city, municipality or zipcode
        biddernro (int) - bidder’s numeric user id
        category (int | string) - category’s id, multiple category id’s can be separated with commas or dashes, 
            eg. 1-2-3
        classification (string - none - ei määritelty, new - uusi, like-new - uudenveroinen, good - hyvä,
            acceptable - tyydyttävä, weak - heikko) - item’s condition. In the API documentation this parameter is
            called condition, but judging by the API response, classification is the actual parameter name.
        closingtime (string - next-day, next-2days, next-5days, next-week) - item’s list time
        feedback_limit (int) - filter by user’s feedback value
        limit (int (50 | 500) - default is 50) - items per page limit
        page (int) - result set page number
        price_max (float) - maximum price
        price_min (float) - minimum price
        seller_type (string - company, user) - seller’s type, default is all.
        sellernro (int) - seller’s numeric user id
        sellstyle (string - all, auction, buy-now) - item’s selling method
        sort (string - hits, newest, closing, lowprice, highprice, bidders, title.
            Default is “hits”.) - result rest sorting
        status (string - open, closed) - item's status
        words (string) - search string

#### get_item_images(itemid)
Retrieve images related to item.

    Args:
        itemid (int) - item's id



#### add_item_image(itemid, image)
Post an image to item.

Item must exist before images can be added.

Item must be in preview or draft state.

Creating an item with draft status is useful if the application wants to save item images before asking
any other parameters from the user. When request status is draft, no additional parameters are required.

    Args:
        itemid (int) - item’s id (already present in the url)
        image (file) - local path to image file


#### delete_item_image(itemid, imageid)
Delete an image from item.

    Args:
        itemid (int) - item’s id
        imageid (int) - image’s id


#### get_item_offers(itemid)
Retrieve information about item’s offers

    Args:
        itemid (int) - item’s id

#### create_item_offer(itemid, offer, message)
Post a new offer (hintaehdotus) to item.

    Args:
        itemid (int) - item’s id
        offer (float) - offer amount (euros), eg. “16.50”
        message (string(255)) - message related to offer

#### answer_item_offer(itemid, offerid, status)
Seller can accept or refuse offers made by users.

Users can cancel offers made by themselves.

Cancelling can only be done if seller has not yet accepted or refused the offer in question.

    Args:
        itemid (int) - item’s id
        offerid (int) - offer’s id
        status (string) - offer status to be updated

#### get_item_questions(itemid)
Retrieve information about item’s questions and seller’s answers.

    Args:
        itemid (int) - item’s id


#### create_item_question(itemid, question)
Post a new offer (hintaehdotus) to item.

    Args:
        itemid (int) - item’s id
        question (string(255)) – question text

#### answer_item_question(itemid, questionid, answer)
Answer to a question. Only seller can post answers.

    Args:
        itemid (int) - item’s id
        questionid (int) - item’s id
        answer (string(255)) - answer text

#### get_user_info()
Retrieve user information.

Note: LastLogin is only visible for the user herself.
Address is only visible for the user herself and for users who have sold items to the user or have bought items from
 the user.
   

#### get_user_settings()
Retrieve user-specific parameter requirements for creating item, e.g. which parameters are allowed or required and
what values are allowed for a certain parameter.
        
#### get_user_feedbacks()
Retrieve user feedbacks.

#### get_user_favorites()
Retrieve user’s favorite items. Also known as “Muistilista”.

#### add_user_favorites(itemid)
Add item to user’s favorite list.

    Args:
        itemid (int) – item id

Note: There is no documented DELETE method to remove favorites!
Note for posterity: Through the web interface, favorites are removed with:
POST https://www.huuto.net/item-favorite/poista/itemid/450185678
And auth token in the headers.


#### get_user_purchases(status='all', post_id=False)
Retrieve items which user has bidded or purchased.

    Args:
        post_id (int) - post’s unique id <<< DOESN'T SEEM TO DO ANYTHING!!!
        status (string) - item’s status - options: open, closed, processing, all


#### get_user_sales(page=1, status='all', sold=0, sort='closing-time', republished='')
Retrieve items created by user.

    Args:
        republished (int - set eg. to 1 to enable filter) - If item is republished or not.
            Effective only if status “open” or “closed” is used at the same time.
        sold (int (0 or 1)) - If item is sold or not.
            Effective only if status “open” or “closed” is used at the same time.
        status (string - all, open, closed, waiting, draft) - item status
        sort (string - bidders, closing-time, current-price, list-time) - result set sorting
        page (int) - result page number

        
## Running the tests

There are two nosetest test scripts:

For testing public API calls: `huuto_test_public.py`
For API calls requiring authentication: `huuto_test_auth.py`

Note that the latter will use the credentials from `huuto_config.ini` and create actual items in Huuto.net (but not publish them).


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Credits
For the sake of mapping the API as close as possible, most of the API Call documentation is taken from the official 
Huuto.net API documentation (http://dev.huuto.net/methods.html) and modified to reflect usage of this client.   