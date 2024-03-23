from mongoengine import Document, StringField, BooleanField, IntField


class StoreModifier(Document):
    id = StringField(primary_key=True)
    name = StringField(required=True)
    description = StringField(required=True)
    symbol = StringField(required=True)
    price = IntField(required=True)
    stacking = BooleanField(required=True)
    timed = BooleanField(required=True)
    duration = IntField(required=True)
    max_stacks = IntField(required=True)

    meta = {'collection': 'modifiers'}
