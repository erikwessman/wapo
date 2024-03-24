from datetime import datetime
from mongoengine import EmbeddedDocument, StringField, IntField, DateTimeField


class PlayerModifier(EmbeddedDocument):
    id = StringField(primary_key=True)
    stacks = IntField(default=0)
    last_used = DateTimeField(default=datetime.utcfromtimestamp(0))
