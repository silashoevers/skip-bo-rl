from ComputerPlayer import ComputerPlayer

import torch

DIM_IN = 193
DIM_OUT = 124
HIDDEN_COUNT = 3
DIM_HIDDEN = 500

class OpponentComputerPlayer(ComputerPlayer):
    def __init__(self, game, model, device, reward_strategy=None, name=""):
        super().__init__(game, model, device, reward_strategy, name)

        self.model_input = torch.zeros(  # NOTE: We doing some bullshit here with card faces compared to offsets
            13  # Hand Cards NOTE: model_input[0] means card 1!
            + 13 * 4  # One hot encodings for each discard pile # here again, card 1 goes to offset 0
            + 13  # One hot encoding for the stock pile # here again, card 1 goes to offset 0
            + 12 * 4
            # One hot encodings for each build pile # HERE IT DOESN'T, we have 12 possible values 0 means that no card is on the stack, max values is 11
            + 1  # Number of stock cards
            # For Opponent:
            + 13 * 4  # One hot encodings for each discard pile # here again, card 1 goes to offset 0
            + 13  # One hot encoding for the stock pile # here again, card 1 goes to offset 0
            + 1  # Number of stock cards
        ).to(device)

    def compute_model_input(self):
        super().compute_model_input()

        opponent = self.game.players[0] if self.game.players[0] != self else self.game.players[1]
        offset = 13 + 4 * 13 + 13 + 12 * 4 + 1
        for discard_pile in range(4):
            if len(opponent.discard_piles[discard_pile]) > 0:
                card = opponent.discard_piles[discard_pile][-1]
                self.model_input[offset + 13 * discard_pile + (12 if card.face == "S" else card.face - 1)] = 1

        offset = 13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4
        top_off_stock = opponent.stock_pile[-1]
        self.model_input[offset + (12 if top_off_stock.face == "S" else top_off_stock.face - 1)] = 1

        offset = 13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4 + 13
        self.model_input[offset] = len(opponent.stock_pile)

    def pretty_print_input(self):
        super().pretty_print_input()

        print("Opponent:")
        print("Discard piles:")
        print("-> Card")
        print("↓ Discard Pile")
        print(self.model_input[13 + 4 * 13 + 13 + 12 * 4 + 1:13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4].view(4, 13))

        print("Stock Card:")
        print("-> Card")
        print(self.model_input[13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4:13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4 + 13])

        print("Number of stock cards:")
        print(self.model_input[13 + 4 * 13 + 13 + 12 * 4 + 1 + 13 * 4 + 13])

    def __str__(self):
        return f"opponent_{self.reward_strategy}"
