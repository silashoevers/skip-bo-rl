import random

from Player import *
from Card import *


class Game:
    def __init__(self, num_human_players, num_computer_players, num_stock_cards=30):
        self.players = []
        for _ in range(num_human_players):
            self.players.append(HumanPlayer(self))
        for _ in range(num_computer_players):
            self.players.append(ComputerPlayer(self))
        random.shuffle(self.players)

        self.draw_pile = [Card(i) for i in range(1, 13) for _ in range(12)] + [Card('S') for _ in range(18)]
        random.shuffle(self.draw_pile)

        self.building_piles = [[], [], [], []]

        self.removed_pile = []

        # Deal cards to the stockpiles of each player
        # We currently do not support playing with 5 or 6 players
        for i in range(num_stock_cards):
            for player in self.players:
                player.stock_pile.append(self.draw_pile.pop())

        # Technically this is not according to the rules, and should be done at the start of each first turn
        for player in self.players:
            player.fill_hand()

        self.is_game_running = True

    # TODO: The game could crash if a player hoards cards
    def draw_card(self):
        if len(self.draw_pile) > 0:
            return self.draw_pile.pop()
        else:
            # Reshuffle
            self.draw_pile = self.removed_pile
            random.shuffle(self.draw_pile)
            for card in self.draw_pile:
                if card.face == 'S':
                    card.value = 0
            self.removed_pile = []

    def get_top_of_build_pile(self, pile_index):
        pile = self.building_piles[pile_index]
        if len(pile) == 0:
            return 0
        else:
            return pile[-1].value

    def start(self):
        current_player_index = 0
        while self.is_game_running:
            print(f"It's the turn of player number {current_player_index}. Go wild.")
            self.players[current_player_index].play()
            current_player_index = (current_player_index + 1) % len(self.players)
        # Check who was the winner based on who has an empty stock pile
        winning_player_index = [player_index for player_index, player in enumerate(self.players) if len(player.stock_pile) == 0][0]
        print(f"Player number {winning_player_index} has won. Congratulations!")
        return

if __name__ == '__main__':
    num_human_players = int(input('How many human players?\n'))
    num_computer_players = int(input('How many computer players?\n'))
    num_stock_cards = int(input('How many stock cards do you want to play with? (Default = 30)\n').strip() or "30")
    game = Game(num_human_players, num_computer_players, num_stock_cards)

    game.start()

