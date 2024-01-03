from mongoengine import Document, IntField, FloatField, StringField, MapField, ListField
from schemas.holding import Holding


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    id = IntField(primary_key=True)
    inventory = MapField(field=IntField(), default=lambda: {})
    coins = FloatField(default=0)
    modifiers = ListField(StringField(), default=list)
    flex_level = IntField(default=0)
    horse_icon = StringField()
    holdings = MapField(field=Holding, default=lambda: {})

    meta = {"collection": "players"}
