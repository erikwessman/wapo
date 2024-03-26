from mongoengine import Document, StringField, BooleanField, IntField


class Product(Document):
    id = StringField(primary_key=True)
    name = StringField(required=True)
    description = StringField(required=True)
    symbol = StringField(required=True)
    price = IntField(required=True)
    is_purchasable = BooleanField(required=True)

    meta = {"abstract": True}
