from mongoengine import Document, DateTimeField, IntField


class HorseRace(Document):
    """
    Represents a horse race
    """

    date = DateTimeField(required=True)
    player = IntField(required=True)
    bet = IntField(required=True)
    win = IntField(required=True)

    meta = {"collection": "horse_races"}
