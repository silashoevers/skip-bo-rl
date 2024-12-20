from Player import Player

import torch
from torch import nn

class ComputerPlayer(Player):
    def __init__(self, game, model, device):
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
            # Could be expanded for Opponents
        ).to(device)

        self.device = device
        self.model = model
        self.num_piles = 4

    def compute_mask(self):
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

    def play(self):
        self.fill_hand()

        end_turn = False
        while not end_turn:
            self.print_game_state()  # TODO: Enable this with a DEBUG flag
            # Assuming for now no exploration, just doing what the model says.
            output = self.model(self.model_input)

            # The assumption is made that recomputing the complete mask and input is fast enough (5ms for computing mask)
            self.compute_mask()
            self.compute_model_input()

            # Mask the output: Only moves that are legal keep their value in the output of the model
            masked_output = output * self.mask
            # TODO: Add Softmax (either before or after mask)
            task = masked_output.argmax().item()  # Vector index maps to the intended move
            if task < 13 * 4:  # Hand to build
                face = "S" if task // 4 == 12 else task // 4 + 1
                build_pile_index = task % 4
                print(f"Hand to build: {face} to {build_pile_index}")
                self.play_hand_to_build(face, build_pile_index)
            elif 13 * 4 <= task < 13 * 4 + 13 * 4:  # Hand to discard
                task -= 13 * 4
                face = "S" if task // 4 == 12 else task // 4 + 1
                discard_pile_index = task % 4
                print(f"Hand to discard: {face} to {discard_pile_index}")
                self.play_hand_to_discard(face, discard_pile_index)
                end_turn = True
            elif 13 * 4 + 13 * 4 <= task < 13 * 4 + 13 * 4 + 4 * 4:  # Discard to build
                task -= 13 * 4 + 13 * 4
                discard_pile_index, build_pile_index = task // 4, task % 4
                print(f"Discard to build: {discard_pile_index}, {build_pile_index}")
                self.play_discard_to_build(discard_pile_index, build_pile_index)
            else:  # Stock to build
                task -= 13 * 4 + 13 * 4 + 4 * 4
                print(f"Stock to build: {task}")
                self.play_stock_to_build(task)

    def pretty_print_mask(self):
        print("Mask:")

        print("Hand to build:")
        print("-> Build index")
        print("↓ Card")
        print(self.mask[:13*4].view(13, 4))

        print("Hand to discard:")
        print("-> Discard index")
        print("↓ Card")
        print(self.mask[13*4:13*4+13*4].view(13, 4))

        print("Discard to Build:")
        print("-> Discard index")
        print("↓ Build index")
        print(self.mask[13*4+13*4:13*4+13*4+4*4].view(4,4))

        print("Stock to build:")
        print("-> Build index")
        print(self.mask[13*4+13*4+4*4:])

    def pretty_print_input(self):
        print("Input:")

        print("Cards:")
        print("-> Card")
        print(self.model_input[:13])

        print("Discard piles:")
        print("-> Card")
        print("↓ Discard Pile")
        print(self.model_input[13:13+13*4].view(4,13))

        print("Stock Card:")
        print("-> Card")
        print(self.model_input[13+13*4:13+13*4+13])

        print("Build piles:")
        print("-> Card")
        print("↓ Build Pile")
        print(self.model_input[13+13*4+13:].view(4,12))

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




