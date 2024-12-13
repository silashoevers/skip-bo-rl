class Card:
    def __init__(self, value, is_joker):
        self.value = value
        self.is_joker = is_joker


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