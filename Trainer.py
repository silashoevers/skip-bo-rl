from collections import deque
import random

from ComputerPlayer import ComputerPlayer, NeuralNetwork
from Game import Game

import torch
import torch.nn as nn
import torch.optim as optim
from tqdm.auto import tqdm

from WinOnlyComputerPlayer import WinOnlyComputerPlayer
from StockComputerPlayer import StockComputerPlayer
from WinStockComputerPlayer import WinStockComputerPlayer
from ComplexComputerPlayer import ComplexComputerPlayer


class Experience(object):
    def __init__(self, state, action, reward, next_state, next_mask):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state # can be None if there is no next state as the game ended
        self.next_mask = next_mask

class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def add(self, experience):
        self.memory.append(experience)

    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        return batch

    def __len__(self):
        return len(self.memory)

BATCH_SIZE = 128
GAMMA = 0.99
TAU = 0.005
NUM_GAMES = 10_000
NUM_COMPUTER_PLAYERS = 2

class Trainer:
    # Based on https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html
    def __init__(self, computer_type, device):
        self.computer_type = computer_type
        self.device = device
        self.memory = ReplayMemory(10_000)
        self.policy_net = NeuralNetwork(127, 124, 2, 500).to(device)
        self.target_net = NeuralNetwork(127, 124, 2, 500).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters())
        self.loss_fn = nn.SmoothL1Loss()

    def optimize_model(self):
        if len(self.memory) < BATCH_SIZE:
            return

        experiences = self.memory.sample(BATCH_SIZE)
        in_states = torch.stack([experience.state for experience in experiences], dim=0).to(self.device)
        actions = torch.stack([torch.tensor([experience.action], dtype=torch.long, device=self.device) for experience in experiences])
        rewards = torch.tensor([experience.reward for experience in experiences], dtype=torch.float, device=self.device)

        non_final = torch.tensor([experience.next_state is not None for experience in experiences], dtype=torch.bool, device=self.device)
        non_final_states = torch.stack(
            [experience.next_state for experience in experiences if experience.next_state is not None], dim=0)
        non_final_masks = torch.stack(
            [experience.next_mask for experience in experiences if experience.next_state is not None], dim=0)

        next_state_rewards = torch.zeros(BATCH_SIZE, dtype=torch.float, device=self.device)
        with torch.no_grad():
            unmasked_next_rewards = self.target_net(non_final_states)
            masked_next_rewards = torch.where(non_final_masks==1, unmasked_next_rewards, float("-inf"))
            next_state_rewards[non_final] = masked_next_rewards.max(1).values
        expected_rewards = rewards + GAMMA * next_state_rewards

        output = self.policy_net(in_states)
        pred_rewards = output.gather(1, actions).squeeze()

        self.optimizer.zero_grad()
        loss = self.loss_fn(pred_rewards, expected_rewards)
        loss.backward()
        self.optimizer.step()

    def train(self):
        for episode in tqdm(range(NUM_GAMES)):
            game = Game(num_human_players=0, num_computer_players=NUM_COMPUTER_PLAYERS, model=self.policy_net,
                        computer_type=self.computer_type, device=self.device, num_stock_cards=30)
            last_experience = [None for _ in range(NUM_COMPUTER_PLAYERS)]
            while game.is_game_running:
                for current_player_index in range(NUM_COMPUTER_PLAYERS):
                    current_player = game.players[current_player_index]
                    current_player.end_turn = False
                    current_player.fill_hand()
                    while not current_player.end_turn and game.is_game_running:
                        current_player.compute_mask()
                        current_player.compute_model_input()
                        if last_experience[current_player_index] is not None:
                            last_experience[current_player_index].next_state = current_player.model_input
                            last_experience[current_player_index].next_mask = current_player.mask
                            self.memory.add(last_experience[current_player_index])
                        in_state = current_player.model_input
                        action, reward = current_player.select_action(training=True, verbose=False)
                        last_experience[current_player_index] = Experience(in_state, action, reward, None, None)

                        self.optimize_model()

                        target_net_state_dict = self.target_net.state_dict()
                        policy_net_state_dict = self.policy_net.state_dict()
                        for key in policy_net_state_dict:
                            target_net_state_dict[key] = policy_net_state_dict[key] * TAU + target_net_state_dict[
                                key] * (1 - TAU)
                        self.target_net.load_state_dict(target_net_state_dict)
            for current_player_index in range(NUM_COMPUTER_PLAYERS):
                current_player = game.players[current_player_index]
                if len(current_player.stock_pile) == 0:
                    self.memory.add(last_experience[current_player_index])
            if (episode + 1) % 100 == 0:
                model_name = str(game.players[0])
                torch.save(self.policy_net.state_dict(), f"models/{model_name}_{episode+1}.pth")


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # TODO add way to pick which model to train/train multiple models at the same time on different devices?
    trainer = Trainer(StockComputerPlayer, device)

    trainer.train()