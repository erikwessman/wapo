from mongoengine import Document, StringField, IntField


class StockPrice(Document):
    """
    Represents a stock price
    """

    ticker = StringField(required=True)
    timestamp = StringField(required=True)
    price = IntField(required=True)

    meta = {"collection": "stock_prices"}
