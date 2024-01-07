from mongoengine import Document, StringField, MapField, IntField


class Roulette(Document):
    """
    Represents a game of roulette
    """

    date = StringField(required=True)
    players = MapField(field=IntField())
    winner = IntField()

    meta = {"collection": "roulette_games"}
