from mongoengine import (
    Document,
    EmbeddedDocumentField,
    IntField,
    StringField,
    MapField,
    ListField,
)
from schemas.holding import Holding


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    id = IntField(primary_key=True)
    inventory = MapField(field=IntField(), default=lambda: {})
    coins = IntField(default=0)
    modifiers = ListField(StringField(), default=list)
    flex_level = IntField(default=0)
    horse_icon = StringField(default="")
    holdings = MapField(EmbeddedDocumentField(Holding), default=lambda: {})

    meta = {"collection": "players"}
