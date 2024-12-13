from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, game):
        self.hand = []
        self.discard_piles = [[], [], [], []]
        self.stock_pile = []
        self.game = game

    @abstractmethod
    def play(self):
        pass

    def fill_hand(self):
        while len(self.hand) < 5:
            self.hand.append(self.game.draw_card())

    def is_face_in_hand(self, card_face):
        return card_face in [card.face for card in self.hand]

    def check_hand_to_build(self, card_face, build_index):
        if self.is_face_in_hand(card_face):
            return card_face == self.game.get_top_of_build_pile(build_index) + 1
        else:
            return False

    def check_hand_to_discard(self, card_face, discard_index):
        return self.is_face_in_hand(card_face)

    def check_discard_to_build(self, discard_index, build_index):
        if len(self.discard_piles[discard_index]) == 0:
            return False
        elif self.discard_piles[discard_index][-1].face == 'S':
            return True
        else:
            return self.discard_piles[discard_index][-1].value == self.game.get_top_of_build_pile(build_index) + 1

    def check_stock_to_build(self, build_index):
        if self.stock_pile[-1].face == 'S':
            return True
        else:
            return self.stock_pile[-1].value == self.game.get_top_of_build_pile(build_index) + 1


class HumanPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

    def play(self):
        pass


class ComputerPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

    def play(self):
        pass
