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
        # Do we want to play a joker
        if card_face == "S" and any([card.is_joker for card in self.hand]):
            return True
        else:
            # Do we have the number card in hand
            return any([card.value == card_face for card in self.hand])

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
        elif self.discard_piles[discard_index][-1].is_joker:
            return True
        else:
            return self.discard_piles[discard_index][-1].value == self.game.get_top_of_build_pile(build_index) + 1

    def check_stock_to_build(self, build_index):
        if self.stock_pile[-1].is_joker:
            return True
        else:
            return self.stock_pile[-1].value == self.game.get_top_of_build_pile(build_index) + 1

    def get_card_from_hand(self, card_face):
        play_card = next(card for card in self.hand if card == card_face)
        self.hand.remove(play_card)
        return play_card

    def play_hand_to_build(self, card_face, build_index):
        play_card = self.get_card_from_hand(card_face)
        build_pile = self.game.building_piles[build_index]
        if play_card.is_joker:
            play_card.value = self.game.get_top_of_build_pile(build_index) + 1
        build_pile.append(play_card)

        if len(self.hand) == 0:
            self.fill_hand()

    def play_hand_to_discard(self, card_face, discard_index):
        play_card = self.get_card_from_hand(card_face)
        discard_pile = self.discard_piles[discard_index]
        discard_pile.append(play_card)

    def play_discard_to_build(self, discard_index, build_index):
        discard_pile = self.discard_piles[discard_index]
        card = discard_pile.pop()
        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)

    def play_stock_to_build(self, build_index):
        card = self.stock_pile.pop()
        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)


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
