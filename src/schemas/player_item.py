from mongoengine import EmbeddedDocument, StringField, IntField


class PlayerItem(EmbeddedDocument):
    id = StringField(primary_key=True)
    amount = IntField(default=1)
