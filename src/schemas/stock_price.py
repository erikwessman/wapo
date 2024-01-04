from mongoengine import Document, StringField, IntField, DateTimeField


class StockPrice(Document):
    """
    Represents a stock price
    """

    ticker = StringField(required=True)
    timestamp = DateTimeField(required=True)
    price = IntField(required=True)

    meta = {"collection": "stock_prices"}
