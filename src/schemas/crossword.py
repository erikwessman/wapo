from mongoengine import Document, StringField, IntField


class Crossword(Document):
    """
    Represents a crossword puzzle with its completion date and score.
    """

    date = StringField(required=True)
    time = IntField(required=True)

    meta = {"collection": "crosswords"}
