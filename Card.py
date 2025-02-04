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
        if isinstance(other, (int, str)):
            return self.face == other
        elif isinstance(other, Card):
            return self.face == other.face
        else:
            return False

    def __str__(self):
        return str(self.face)