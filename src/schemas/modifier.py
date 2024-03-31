from mongoengine import BooleanField, IntField

from schemas.product import Product


class Modifier(Product):
    is_stacking = BooleanField(required=True)
    is_timed = BooleanField(required=True)
    duration = IntField(required=True)
    max_stacks = IntField(required=True)

    meta = {"collection": "modifiers"}
