from mongoengine import (
    Document,
    EmbeddedDocumentField,
    IntField,
    StringField,
    MapField
)
from schemas.modifier import Modifier
from schemas.holding import Holding
from schemas.avatar import Avatar


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    id = IntField(primary_key=True)
    inventory = MapField(field=IntField(), default=lambda: {})
    coins = IntField(default=0)
    modifiers = MapField(EmbeddedDocumentField(Modifier), default=lambda: {})
    active_avatar = StringField(default="")
    avatars = MapField(EmbeddedDocumentField(Avatar), default=lambda: {})
    holdings = MapField(EmbeddedDocumentField(Holding), default=lambda: {})

    meta = {"collection": "players"}
