from mongoengine import Document, StringField, BooleanField, IntField


class StoreItem(Document):
    id = StringField(primary_key=True)
    name = StringField(required=True)
    description = StringField(required=True)
    symbol = StringField(required=True)
    price = IntField(required=True)
    one_time_use = BooleanField(required=True, default=True)
    on_sale = BooleanField(default=False)

    meta = {"collection": "items"}
