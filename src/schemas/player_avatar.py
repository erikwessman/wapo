from mongoengine import EmbeddedDocument, StringField, IntField


class PlayerAvatar(EmbeddedDocument):
    """
    Represents a player's avatar
    """

    icon = StringField(required=True)
    rarity = StringField(required=True)
    count = IntField(default=1)
