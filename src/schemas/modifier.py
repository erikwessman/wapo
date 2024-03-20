from mongoengine import EmbeddedDocument, StringField, DateTimeField, IntField


class Modifier(EmbeddedDocument):
    """
    Represents a modifier
    """

    name = StringField(required=True)
    amount = IntField(required=True)
    last_used = DateTimeField()
