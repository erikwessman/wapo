from mongoengine import EmbeddedDocument, StringField, IntField


class Avatar(EmbeddedDocument):
    """
    Represents a player's avatar
    """

    icon = StringField(required=True)
    rarity = StringField(required=True)
    count = IntField(required=True)
