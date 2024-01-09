from mongoengine import Document, DateTimeField, MapField, IntField


class Roulette(Document):
    """
    Represents a game of roulette
    """

    date = DateTimeField(required=True)
    players = MapField(field=IntField(), required=True)
    winner = IntField(required=True)

    meta = {"collection": "roulette_games"}
