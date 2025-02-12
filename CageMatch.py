import datetime
import itertools
import logging
import os
import re

import torch
from tqdm import tqdm
import pandas as pd

import ComputerPlayer as CP
import OpponentComputerPlayer as OCP
from ComputerPlayer import NeuralNetwork
from Game import Game
from RandomComputerPlayer import RandomComputerPlayer
from reward_strategies.WinOnlyRewardStrategy import WinOnlyRewardStrategy

NUM_GAMES = 100
NUM_COMPUTER_PLAYERS = 2
NUM_CARDS = 30


class Tester:
    def __init__(self, computers, reward_strategies, device_used, models, names, num_comp_players=NUM_COMPUTER_PLAYERS,
                 num_cards=NUM_CARDS, num_games=NUM_GAMES):
        self.computer_types = computers
        self.reward_strategies = reward_strategies
        self.device = device_used
        self.models = models
        self.names = names
        self.num_comp_players = num_comp_players
        self.num_cards = num_cards
        self.num_games = num_games

    def test(self):
        game_winners = {key: 0 for key in self.names}
        game_winners['lost'] = 0
        action_list = []
        for i in range(self.num_games):
            game = Game(num_human_players=0, num_computer_players=self.num_comp_players, model=self.models,
                        names=self.names, computer_type=self.computer_types,
                        reward_strategy=self.reward_strategies, device=self.device,
                        num_stock_cards=self.num_cards)
            current_player_index = 0
            turns = 0
            while game.is_game_running:
                if current_player_index == 0:
                    turns += 1
                game.players[current_player_index].play()
                current_player_index = (current_player_index + 1) % len(game.players)
            if len(game.draw_pile) == 0:
                game_winners['lost'] += 1
            else:
                # Check who was the winner based on who has an empty stock pile
                winning_player = [player for player in game.players if len(player.stock_pile) == 0][0]
                game_winners[winning_player.name] += 1
            action_list.append(self.names + [i, turns] + [player.actions for player in game.players])
        return game_winners, action_list


def run_tests(test_these_models, num_comp_players=NUM_COMPUTER_PLAYERS,
              num_cards=NUM_CARDS, num_games=NUM_GAMES):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logname = os.path.join('TestResults',
                           ("cageMatchTest" + datetime.datetime.now().strftime("%d%m%Y-%H%M%S") + ".log"))
    logging.basicConfig(filename=logname, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)
    print("loading models")
    models_to_test = []
    # structure for training
    logger.debug("Testing following models: ")
    for model_name in tqdm(test_these_models):
        opponent = "opponent" in model_name
        if opponent:
            model = NeuralNetwork(OCP.DIM_IN,
                                  OCP.DIM_OUT,
                                  OCP.HIDDEN_COUNT,
                                  OCP.DIM_HIDDEN).to(device)
        else:
            model = NeuralNetwork(CP.DIM_IN,
                                  CP.DIM_OUT,
                                  CP.HIDDEN_COUNT,
                                  CP.DIM_HIDDEN).to(device)
        model.load_state_dict(torch.load(os.path.join('models', model_name), weights_only=True, map_location='cuda'))
        model.eval()
        models_to_test.append((model, model_name, opponent))
        logger.info(model_name)
    win_results = []
    action_results = []
    print("Testing against randoms")
    # only using one type of ComputerPlayer since the difference between players is their reward
    logger.debug("vs Random tests")
    for (model, name, opponent) in tqdm(models_to_test):
        tester = Tester(computers=[RandomComputerPlayer, OCP.OpponentComputerPlayer if opponent else CP.ComputerPlayer],
                        device_used=device, models=['', model],
                        reward_strategies=[WinOnlyRewardStrategy, WinOnlyRewardStrategy], names=["Random", name],
                        num_comp_players=num_comp_players, num_cards=num_cards, num_games=num_games)
        game_winners, action_list = tester.test()
        win_results.append(game_winners)
        action_results += action_list
    print("Testing against each other")
    matches = list(itertools.combinations(models_to_test, 2))
    logger.debug("Cage match models")
    for ((model1, name1, opponent1), (model2, name2, opponent2)) in tqdm(matches):
        computer_types = [OCP.OpponentComputerPlayer if opponent1 else CP.ComputerPlayer,
                          OCP.OpponentComputerPlayer if opponent2 else CP.ComputerPlayer]
        tester = Tester(computers=computer_types, device_used=device, models=[model1, model2],
                        reward_strategies=[WinOnlyRewardStrategy, WinOnlyRewardStrategy], names=[name1, name2],
                        num_comp_players=num_comp_players, num_cards=num_cards, num_games=num_games)
        game_winners, action_list = tester.test()
        win_results.append(game_winners)
        action_results += action_list
    logger.debug("Tests finished")

    # Write the win results to a csv file
    win_results_df = pd.DataFrame(columns=test_these_models + ["Random"], index=test_these_models + ["Random"])
    for m in win_results:
        logger.info(m)
        player_1, player_2 = [name for name in m.keys() if name != "lost"]
        win_results_df.loc[player_1, player_2] = m[player_1]
        win_results_df.loc[player_2, player_1] = m[player_2]
    win_csv_name = logname.replace(".log", "_win.csv")
    win_results_df.to_csv(win_csv_name, index=False)

    # Write the action results to a csv
    action_results_df = pd.DataFrame(data=action_results,
                                     columns=["Player 1", "Player 2", "Game Number", "Turns", "Player 1 Actions Count",
                                              "Player 2 Actions Count"])
    actions_csv_name = logname.replace(".log", "_actions.csv")
    action_results_df.to_csv(actions_csv_name, index=False)


if __name__ == "__main__":
    all_models = sorted(os.listdir("models"),
                        key=lambda x: ("_".join(x.split("_")[:-1]), int(re.search("[0-9]+", x)[0])))
    models = []
    prev = all_models[0]
    for model in all_models[1:]:
        if model.split("_")[:-1] != prev.split("_")[:-1]:
            models.append(prev)
        prev = model
    models.append(prev)
    run_tests(models)
