import math
import random

from Player import Player

import torch
from torch import nn

DIM_IN = 127
DIM_OUT = 124
HIDDEN_COUNT = 3
DIM_HIDDEN = 500

WIN_REWARD = 100
LOSS_REWARD = -100
STOCK_REWARD = 1
DISCARD_REWARD = -0.5

EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000

class ComputerPlayer(Player):
    def __init__(self, game, model, device, reward_strategy=None, name=""):
        super().__init__(game)
        self.mask = torch.zeros(
            # NOTE: IN THE MASK, ALL CARDS ARE MAPPED TO ONE LOWER, so card 1 is in offset 0 of the mask
            13 * 4  # For every card to every build pile, so first card 1 to build 0, then card 1 to build 1 etc.
            + 13 * 4  # For every card to every discard pile, so first card 1 to discard 0, then card 1 to discard 1 etc.
            + 4 * 4  # From every discard pile to every build pile, so discard 0 to build 0, then discard 0 to build 1 etc.
            + 4  # From stock pile to every build pile, so first stock to build 0, then stock to build 1
        ).to(device)

        self.model_input = torch.zeros(  # NOTE: We doing some bullshit here with card faces compared to offsets
            13  # Hand Cards NOTE: model_input[0] means card 1!
            + 13 * 4  # One hot encodings for each discard pile # here again, card 1 goes to offset 0
            + 13  # One hot encoding for the stock pile # here again, card 1 goes to offset 0
            + 12 * 4
            # One hot encodings for each build pile # HERE IT DOESN'T, we have 12 possible values 0 means that no card is on the stack, max values is 11
            + 1  # Number of stock cards
            # Could be expanded for Opponents
        ).to(device)

        self.reward_strategy = reward_strategy
        if self.reward_strategy is not None:
            self.reward_strategy.register_player(self)

        self.device = device
        self.model = model
        self.num_piles = 4

        self.end_turn = False
        self.name = name

    def compute_mask(self):
        self.mask.zero_()
        for card in range(13):
            for pile in range(4):
                card_face = 'S' if card == 12 else card + 1
                self.mask[self.num_piles * card + pile] = self.check_hand_to_build(card_face, pile)
        offset = 13 * 4
        for card in range(13):
            card_face = 'S' if card == 12 else card + 1
            self.mask[offset + self.num_piles * card:
                      offset + self.num_piles * card + self.num_piles] = self.check_hand_to_discard(
                card_face, 0)  # Only need to check for 1, not for all piles, as it does not depend on the pile
        offset = 13 * 4 + 13 * 4
        for discard_pile in range(4):
            for build_pile in range(4):
                self.mask[offset + self.num_piles * discard_pile + build_pile] = self.check_discard_to_build(
                    discard_pile, build_pile)
        offset = 13 * 4 + 13 * 4 + 4 * 4
        for build_pile in range(4):
            self.mask[offset + build_pile] = self.check_stock_to_build(build_pile)

    def compute_model_input(self):
        self.model_input.zero_()
        for card in self.hand:
            self.model_input[12 if card.face == "S" else card.face - 1] += 1

        offset = 13
        for discard_pile in range(4):
            if len(self.discard_piles[discard_pile]) > 0:
                card = self.discard_piles[discard_pile][-1]
                self.model_input[offset + 13 * discard_pile + (12 if card.face == "S" else card.face - 1)] = 1

        offset = 13 + 13 * 4
        top_off_stock = self.stock_pile[-1]
        self.model_input[offset + (12 if top_off_stock.face == "S" else top_off_stock.face - 1)] = 1

        offset = 13 + 4 * 13 + 13
        for build_pile in range(4):
            card = self.game.get_top_of_build_pile(build_pile)
            self.model_input[offset + 12 * build_pile + card] = 1

        offset = 13 + 4 * 13 + 13 + 12 * 4
        self.model_input[offset] = len(self.stock_pile)

    def select_action(self, training, verbose, steps_done):
        eps_threshold = EPS_END + (EPS_START - EPS_END) * math.exp(-steps_done / EPS_DECAY)
        if training and random.random() < eps_threshold:
            action = torch.multinomial(self.mask, 1).item()
        else:
            with torch.no_grad():
                output = self.model(self.model_input)
                masked_output = torch.where(self.mask == 1, output, float("-inf"))
                if verbose:
                    self.pretty_print_output(masked_output)
                action = masked_output.argmax().item()
        return action

    def select_and_do_action(self, training, steps_done, verbose=False):
        """
        Returns reward if training is enabled
        """
        reward = 0  # Justin Case

        action = self.select_action(training, verbose, steps_done)

        selected_action = action
        if action < 13 * 4:  # Hand to build
            face = "S" if action // 4 == 12 else action // 4 + 1
            build_pile_index = action % 4
            if training:
                reward = self.reward_strategy.reward_hand_to_build(face, build_pile_index)
            else:
                self.play_hand_to_build(face, build_pile_index)
        elif 13 * 4 <= action < 13 * 4 + 13 * 4:  # Hand to discard
            action -= 13 * 4
            face = "S" if action // 4 == 12 else action // 4 + 1
            discard_pile_index = action % 4
            if training:
                reward = self.reward_strategy.reward_hand_to_discard(face, discard_pile_index)
            else:
                self.play_hand_to_discard(face, discard_pile_index)
            self.end_turn = True
        elif 13 * 4 + 13 * 4 <= action < 13 * 4 + 13 * 4 + 4 * 4:  # Discard to build
            action -= 13 * 4 + 13 * 4
            discard_pile_index, build_pile_index = action // 4, action % 4
            if training:
                reward = self.reward_strategy.reward_discard_to_build(discard_pile_index, build_pile_index)
            else:
                self.play_discard_to_build(discard_pile_index, build_pile_index)
        else:  # Stock to build
            action -= 13 * 4 + 13 * 4 + 4 * 4
            if training:
                reward = self.reward_strategy.reward_stock_to_build(action)
            else:
                self.play_stock_to_build(action)
            if len(self.stock_pile) < 1:
                self.game.is_game_running = False

        if training:
            return selected_action, reward

    def play(self):
        self.fill_hand()

        self.end_turn = False
        while not self.end_turn and self.game.is_game_running:
            self.compute_mask()
            self.compute_model_input()
            # self.print_game_state()  # TODO: Enable this with a DEBUG flag
            self.select_and_do_action(training=False, verbose=False, steps_done=0)

    def pretty_print_mask(self):
        print("Mask:")

        print("Hand to build:")
        print("-> Build index")
        print("↓ Card")
        print(self.mask[:13 * 4].view(13, 4))

        print("Hand to discard:")
        print("-> Discard index")
        print("↓ Card")
        print(self.mask[13 * 4:13 * 4 + 13 * 4].view(13, 4))

        print("Discard to Build:")
        print("-> Discard index")
        print("↓ Build index")
        print(self.mask[13 * 4 + 13 * 4:13 * 4 + 13 * 4 + 4 * 4].view(4, 4))

        print("Stock to build:")
        print("-> Build index")
        print(self.mask[13 * 4 + 13 * 4 + 4 * 4:])

    def pretty_print_output(self, output):
        print("Ouput:")

        print("Hand to build:")
        print("-> Build index")
        print("↓ Card")
        print(output[:13 * 4].view(13, 4))

        print("Hand to discard:")
        print("-> Discard index")
        print("↓ Card")
        print(output[13 * 4:13 * 4 + 13 * 4].view(13, 4))

        print("Discard to Build:")
        print("-> Discard index")
        print("↓ Build index")
        print(output[13 * 4 + 13 * 4:13 * 4 + 13 * 4 + 4 * 4].view(4, 4))

        print("Stock to build:")
        print("-> Build index")
        print(output[13 * 4 + 13 * 4 + 4 * 4:])

    def pretty_print_input(self):
        print("Input:")

        print("Cards:")
        print("-> Card")
        print(self.model_input[:13])

        print("Discard piles:")
        print("-> Card")
        print("↓ Discard Pile")
        print(self.model_input[13:13 + 13 * 4].view(4, 13))

        print("Stock Card:")
        print("-> Card")
        print(self.model_input[13 + 13 * 4:13 + 13 * 4 + 13])

        print("Build piles:")
        print("-> Card")
        print("↓ Build Pile")
        print(self.model_input[13 + 13 * 4 + 13:13 + 13 * 4 + 13 + 12 * 4].view(4, 12))

        print("Number of stock cards:")
        print(self.model_input[13 + 13 * 4 + 13 + 12 * 4])

    def __str__(self):
        return self.reward_strategy.__str__()


class NeuralNetwork(nn.Module):
    def __init__(self, dim_in, dim_out, num_hidden_layers, dim_hidden):
        super().__init__()
        hidden_layers = []
        for i in range(num_hidden_layers):
            in_size = dim_in if i == 0 else dim_hidden
            hidden_layers.append(nn.Linear(in_size, dim_hidden))
            hidden_layers.append(nn.ReLU())
        self.linear_relu_stack = nn.Sequential(*hidden_layers)
        self.output_layer = nn.Linear(dim_hidden, dim_out)

    def forward(self, x):
        logits = self.linear_relu_stack(x)  # Probabilities passed along the hidden layers
        return self.output_layer(logits)
