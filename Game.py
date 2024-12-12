import random

from Player import *
from Card import *


class Game:
    def __init__(self, num_human_players, num_computer_players):
        self.players = []
        for _ in range(num_human_players):
            self.players.append(HumanPlayer(self))
        for _ in range(num_computer_players):
            self.players.append(ComputerPlayer(self))
        random.shuffle(self.players)

        self.draw_pile = [Card(i, False) for i in range(1, 13) for _ in range(12)] + [Card(0, True) for _ in range(18)]
        random.shuffle(self.draw_pile)

        self.building_piles = [[], [], [], []]

        self.removed_pile = []

        # Deal cards to the stockpiles of each player
        # We currently do not support playing with 5 or 6 players
        for i in range(30):
            for player in self.players:
                player.stock_pile.append(self.draw_pile.pop())

        # Technically this is not according to the rules, and should be done at the start of each first turn
        for player in self.players:
            player.fill_hand()

    # TODO: The game could crash if a player hoards cards
    def draw_card(self):
        if len(self.draw_pile) > 0:
            return self.draw_pile.pop()
        else:
            # Reshuffle
            self.draw_pile = self.removed_pile
            random.shuffle(self.draw_pile)
            for card in self.draw_pile:
                if card.is_joker:
                    card.value = 0
            self.removed_pile = []

    def get_top_of_build_pile(self, pile_index):
        pile = self.building_piles[pile_index]
        if len(pile) == 0:
            return 0
        else:
            return pile[-1].value
