import os
import random
import torch

from Player import *
import ComputerPlayer as CP
import OpponentComputerPlayer as OCP
from Card import *
from WinOnlyRewardStrategy import WinOnlyRewardStrategy


class Game:

    def __init__(self, num_human_players, num_computer_players, model, names, computer_type, reward_strategy, device,
                 num_stock_cards=30):
        """
        :param num_human_players:
        :param num_computer_players:
        :param model: Pytorch model(s)
        :param computer_type: Specific subclass of ComputerPlayer
        :param device:
        :param num_stock_cards:
        """
        self.players = []
        if model is None:
            model = CP.NeuralNetwork(127, 124, 4, 500).to(device)
        if isinstance(model, list):
            assert len(model) == num_computer_players
            assert len(computer_type) == num_computer_players
            assert len(reward_strategy) == num_computer_players
            for i in range(num_computer_players):
                self.players.append(
                    computer_type[i](self, model=model[i], device=device, reward_strategy=reward_strategy[i](),
                                     name=names[i]))
        else:
            for _ in range(num_computer_players):
                self.players.append(computer_type(self, model=model, device=device, reward_strategy=reward_strategy()))

        for _ in range(num_human_players):
            self.players.append(HumanPlayer(self))
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

    # TODO: The game could crash if a player hoards cards. Fix this.
    def draw_card(self):
        if len(self.draw_pile) == 0:
            # Reshuffle
            self.draw_pile = self.removed_pile
            random.shuffle(self.draw_pile)
            for card in self.draw_pile:
                if card.face == 'S':
                    card.value = 0
            self.removed_pile = []
        if len(self.draw_pile) == 0:
            self.is_game_running = False
            return Card(-1)
        return self.draw_pile.pop()

    def get_top_of_build_pile(self, pile_index):
        pile = self.building_piles[pile_index]
        if len(pile) == 0:
            return 0
        else:
            return pile[-1].value

    def clear_build_pile_if_full(self, pile_index):
        pile = self.building_piles[pile_index]
        if len(pile) == 12:
            self.removed_pile.extend(pile)
            self.building_piles[pile_index] = []

    def start(self):
        current_player_index = 0
        while self.is_game_running:
            print(f"It's the turn of player number {current_player_index}. Go wild.")
            self.players[current_player_index].play()
            current_player_index = (current_player_index + 1) % len(self.players)
        if len(self.draw_pile) == 0:
            print("Everyone lost")
        else:
            # Check who was the winner based on who has an empty stock pile
            winning_player_index = \
                [player_index for player_index, player in enumerate(self.players) if len(player.stock_pile) == 0][0]
            print(f"Player number {winning_player_index} has won. Congratulations!")


if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    num_human_players = int(input('How many human players?\n'))
    # Hack to allow training with older Python version
    if num_human_players > 0:
        from HumanPlayer import HumanPlayer
    num_computer_players = int(input('How many computer players?\n'))
    num_stock_cards = int(input('How many stock cards do you want to play with? (Default = 30)\n').strip() or "30")
    model_name = input('Please enter a model name:\n')
    opponent = model_name.startswith("opponent")
    if opponent:
        model = CP.NeuralNetwork(OCP.DIM_IN,
                                 OCP.DIM_OUT,
                                 OCP.HIDDEN_COUNT,
                                 OCP.DIM_HIDDEN).to(device)
    else:
        model = CP.NeuralNetwork(CP.DIM_IN,
                                 CP.DIM_OUT,
                                 CP.HIDDEN_COUNT,
                                 CP.DIM_HIDDEN).to(device)
    model.load_state_dict(torch.load(os.path.join("models", model_name), weights_only=True))
    model.eval()
    names = [f'computer_player_{i}' for i in range(num_computer_players)]
    names += [f'human_player_{i}' for i in range(num_human_players)]
    computer_type = OCP.OpponentComputerPlayer if opponent else CP.ComputerPlayer
    game = Game(num_human_players, num_computer_players, model, names, computer_type, WinOnlyRewardStrategy, device,
                num_stock_cards)

    game.start()
