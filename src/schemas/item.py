from mongoengine import BooleanField

from schemas.product import Product


class Item(Product):
    one_time_use = BooleanField(required=True, default=True)
    on_sale = BooleanField(default=False)

    meta = {"collection": "items"}
