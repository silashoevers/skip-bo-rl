from abc import ABC, abstractmethod

import Card

class Player(ABC):
    hand: list[Card.Card]
    discard_piles: list[list[Card.Card]]
    stock_pile: list[Card.Card]

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
            if card_face == 'S':
                return True
            else:
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

    def get_card_from_hand(self, card_face):
        play_card = next(card for card in self.hand if card == card_face)
        self.hand.remove(play_card)
        return play_card

    def play_hand_to_build(self, card_face, build_index):
        play_card = self.get_card_from_hand(card_face)
        build_pile = self.game.building_piles[build_index]
        if play_card.face == 'S':
            play_card.value = self.game.get_top_of_build_pile(build_index) + 1
        build_pile.append(play_card)

        self.game.clear_build_pile_if_full(build_index)

        if len(self.hand) == 0:
            self.fill_hand()

    def play_hand_to_discard(self, card_face, discard_index):
        play_card = self.get_card_from_hand(card_face)
        discard_pile = self.discard_piles[discard_index]
        discard_pile.append(play_card)

    def play_discard_to_build(self, discard_index, build_index):
        discard_pile = self.discard_piles[discard_index]
        card = discard_pile.pop()

        if card.face == 'S':
            card.value = self.game.get_top_of_build_pile(build_index) + 1

        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)

        self.game.clear_build_pile_if_full(build_index)

    def play_stock_to_build(self, build_index):
        card = self.stock_pile.pop()

        if card.face == 'S':
            card.value = self.game.get_top_of_build_pile(build_index) + 1

        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)

        self.game.clear_build_pile_if_full(build_index)

    def print_game_state(self):
        # TODO: Add opponent game state (Scale up to 3 other players)
        # TODO: Add index indicator for build and discard piles
        # TODO: Show complete discard pile contents (not just top card)
        # Building pile top cards.
        tops_of_build_piles = [self.game.get_top_of_build_pile(pile_index) for pile_index in range(0,4)]
        print("  ".join([f"[{top if top > 0 else '_'}]" for top in tops_of_build_piles]))
        print()
        # Discard piles. Only show top card per pile.
        print(f"[{self.stock_pile[-1]}]]  " + " ".join([f"[{self.discard_piles[pile_index][-1] if len(self.discard_piles[pile_index]) > 0 else '_'}]" for pile_index in range(0,4)]))
        print('----------------------')
        # Hand and stock
        print("=> " + " ".join([f"[{card}]" for card in self.hand]) + " <=")
        print()
