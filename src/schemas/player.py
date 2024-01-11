from mongoengine import (
    Document,
    EmbeddedDocumentField,
    IntField,
    StringField,
    MapField,
    ListField,
)
from schemas.holding import Holding
from schemas.avatar import Avatar


class Player(Document):
    """
    Represents a player/user in the Discord server
    """

    id = IntField(primary_key=True)
    inventory = MapField(field=IntField(), default=lambda: {})
    coins = IntField(default=0)
    modifiers = ListField(StringField(), default=list)
    flex_level = IntField(default=0) # TODO: remove. no longer used but bot breaks if removed
    active_avatar = StringField(default="")
    avatars = MapField(EmbeddedDocumentField(Avatar), default=lambda: {})
    holdings = MapField(EmbeddedDocumentField(Holding), default=lambda: {})

    meta = {"collection": "players"}
