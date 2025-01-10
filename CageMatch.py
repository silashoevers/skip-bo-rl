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
MODELS_TO_TEST = ['complex_computer_player_100.pth']

class Tester:

    def __init__(self, computer_types, device, models):
        self.computer_types = computer_types
        self.device = device
        self.models = models

    def test(self):
        game_winners = {key: 0 for key in self.computer_types}
        game_winners['lost'] = 0
        for _ in tqdm(range(NUM_GAMES)):
            game = Game(num_human_players=0, num_computer_players=NUM_COMPUTER_PLAYERS, model=self.models,
                        computer_type=self.computer_type, device=self.device, num_stock_cards=NUM_CARDS)
            current_player_index=0
            while game.is_game_running:
                game.players[current_player_index].play()
                current_player_index = (current_player_index + 1) % len(game.players)
            if len(game.draw_pile) == 0:
                print("Everyone lost")
                game_winners['lost'] +=1
            else:
                # Check who was the winner based on who has an empty stock pile
                winning_player = [player for player in game.players if len(player.stock_pile) == 0][0]
                game_winners[winning_player.type] += 1
        return game_winners





if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    models_to_test = []
    computer_types = [] #only using one type of ComputerPlayer since the difference between players is their reward structure for training
    for model_name in MODELS_TO_TEST:
        model = NeuralNetwork(127, 124, 2, 500).to(device)
        model.load_state_dict(torch.load(os.path.join("models", model_name), weights_only=True))
        model.eval()
        models_to_test.append(model)
    results = []
    print("Testing against randoms")
    for i in len(models_to_test):
        tester = Tester([RandomComputerPlayer,WinOnlyComputerPlayer], device, ['', models_to_test[i]])
        results.append(tester.test())
    print(results)
    print("Testing against each other")
    matches = itertools.combinations(models_to_test, 2)
    matchResults = {key:None for key in matches}
    for match in matches:
        tester = Tester([WinOnlyComputerPlayer,WinOnlyComputerPlayer], device, list(match))
        matchResults[match] = tester.test()
    print(matchResults)