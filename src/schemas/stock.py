from mongoengine import Document, StringField


class Stock(Document):
    """
    Represents a single company stock
    """

    ticker = StringField(primary_key=True)
    company = StringField(required=True)

    meta = {"collection": "stocks"}
