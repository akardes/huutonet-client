import huuto


###################################################
# Helpers
###################################################
def get_random_item_id():
    """For some tests we need a random existing item"""
    items = huuto.get_category_items(1)

    return items['items'][0]['id']

