class Card:
    """
    value: The value that a card has in a given context. SkipBo cards (jokers) get assigned their contextual value in a build pile
    face:  Possible faces are 1,2,..,11,12 and 'S'. Used to address a card when trying to play it.
    """
    def __init__(self, face):
        self.face = face
        if isinstance(face, int):
            self.value = face
        else:  # Face == 'S'
            self.value = 0

    # Method used to give joker the value used in a building pile
    def set_value(self, value):
        self.value = value

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        if isinstance(other, str) and other == "S":
            return self.is_joker
        elif isinstance(other, Card):
            return self.value == other.value
        else:
            return False