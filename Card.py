class Card:
    def __init__(self, value, is_joker):
        self.value = value
        self.is_joker = is_joker


    # Method used to give joker the value used in a building pile
    def set_value(self, value):
        self.value = value
