from mongoengine import EmbeddedDocument, StringField, BooleanField, IntField


class Item(EmbeddedDocument):
    """
    Represents an inventory item
    """

    id = StringField(required=True)
    name = StringField(required=True)
    description = StringField()
    one_time_use = BooleanField(required=True)
    price = IntField(required=True)
    symbol = StringField()
