from mongoengine import EmbeddedDocument, StringField, IntField, FloatField


class PlayerHolding(EmbeddedDocument):
    """
    Represents a player's holding
    """

    ticker = StringField(required=True)
    shares = IntField(required=True)
    average_price = FloatField(required=True)
