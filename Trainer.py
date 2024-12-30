from collections import deque
import random

from ComputerPlayer import ComputerPlayer, NeuralNetwork

import torch
import torch.nn as nn
import torch.optim as optim

class Experience(object):
    def __init__(self, state, action, reward, next_state):
        self.state = state
        self.action = action
        self.reward = reward
        self.next_state = next_state # can be None if there is no next state as the game ended

class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state):
        experience = Experience(state, action, reward, next_state)
        self.memory.append(experience)

    def sample(self, batch_size):
        batch = random.sample(self.memory, batch_size)
        return batch

    def __len__(self):
        return len(self.memory)

BATCH_SIZE = 128
GAMMA = 0.99

class Trainer:
    def __init__(self, device):
        self.memory = ReplayMemory(10000)
        self.policy_net = NeuralNetwork(126, 124, 2, 500).to(device)
        self.target_net = NeuralNetwork(126, 124, 2, 500).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters())
        self.loss_fn = nn.SmoothL1Loss()

    def optimize_model(self):
        if len(self.memory) < BATCH_SIZE:
            return

        experiences = self.memory.sample(BATCH_SIZE)
        in_states = torch.stack([experience.in_state for experience in experiences], dim=0)
        actions = torch.tensor([experience.action for experience in experiences], dtype=torch.long)
        rewards = torch.tensor([experience.reward for experience in experiences], dtype=torch.float)

        non_final = torch.tensor([experience.next_state is not None for experience in experiences], dtype=torch.bool)
        non_final_states = torch.stack(
            [experience.next_state for experience in experiences if experience.next_state is not None], dim=0)

        next_state_rewards = torch.zeros(BATCH_SIZE, dtype=torch.float)
        with torch.no_grad():
            next_state_rewards[non_final] = self.target_net(non_final_states).max(1).values
        expected_rewards = rewards + GAMMA * next_state_rewards

        pred_rewards = self.policy_net(in_states).gather(1, actions)

        self.optimizer.zero_grad()
        loss = self.loss_fn(pred_rewards, expected_rewards)
        loss.backward()
        self.optimizer.step()

    def train(self):
        # TODO: Write
        pass
