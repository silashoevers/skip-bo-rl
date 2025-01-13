import itertools
import os

import torch
from tqdm import tqdm

from ComputerPlayer import NeuralNetwork
from Game import Game
from RandomComputerPlayer import RandomComputerPlayer
from WinOnlyComputerPlayer import WinOnlyComputerPlayer

NUM_GAMES = 100
NUM_COMPUTER_PLAYERS = 2
NUM_CARDS = 30
MODELS_TO_TEST = ['complex_computer_player_10000.pth',
                  'discard_computer_player_10000.pth',
                  'discard_stock_computer_player_10000.pth',
                  'discard_win_computer_player_10000.pth',
                  'stock_computer_player_10000.pth',
                  'win_stock_computer_player_10000.pth'
                  ]


class Tester:
    def __init__(self, computers, device_used, models, names):
        self.computer_types = computers
        self.device = device_used
        self.models = models
        self.names = names

    def test(self):
        game_winners = {key: 0 for key in self.names}
        game_winners['lost'] = 0
        for _ in range(NUM_GAMES):
            game = Game(num_human_players=0, num_computer_players=NUM_COMPUTER_PLAYERS, model=self.models,
                        names=self.names, computer_type=self.computer_types, device=self.device,
                        num_stock_cards=NUM_CARDS)
            current_player_index = 0
            while game.is_game_running:
                game.players[current_player_index].play()
                current_player_index = (current_player_index + 1) % len(game.players)
            if len(game.draw_pile) == 0:
                game_winners['lost'] += 1
            else:
                # Check who was the winner based on who has an empty stock pile
                winning_player = [player for player in game.players if len(player.stock_pile) == 0][0]
                game_winners[winning_player.name] += 1
        return game_winners


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("loading models")
    models_to_test = []
    computer_types = []  # only using one type of ComputerPlayer since the difference between players is their reward
    # structure for training
    for model_name in tqdm(MODELS_TO_TEST):
        model = NeuralNetwork(127, 124, 3, 500).to(device)
        model.load_state_dict(torch.load(os.path.join('models', model_name), weights_only=True))
        model.eval()
        models_to_test.append((model, model_name))
    results = []
    print("Testing against randoms")
    for model in tqdm(models_to_test):
        tester = Tester(computers=[RandomComputerPlayer, WinOnlyComputerPlayer], device_used=device, models=['', model[0]], names=["Random",model[1]])
        results.append(tester.test())
    for r in results:
        print(r)
    print("Testing against each other")
    matches = list(itertools.combinations(models_to_test, 2))
    matchResults = []
    for match in tqdm(matches):
        tester = Tester(computers=[WinOnlyComputerPlayer, WinOnlyComputerPlayer], device_used=device, models=[list(match)[0][0], list(match)[1][0]], names=[list(match)[0][1], list(match)[1][1]])
        matchResults.append(tester.test())
    for m in matchResults:
        print(m)
