import torch

from ComputerPlayer import ComputerPlayer


class RandomComputerPlayer(ComputerPlayer):
    def reward_hand_to_discard(self, card_face, discard_index):
        self.play_hand_to_discard(card_face, discard_index)
        return 0

    def reward_discard_to_build(self, discard_index, build_index):
        self.play_discard_to_build(discard_index, build_index)
        return 0

    def reward_hand_to_build(self, card_face, build_index):
        self.play_hand_to_build(card_face, build_index)
        return 0

    def reward_stock_to_build(self, build_index):
        self.play_stock_to_build(build_index)
        return 0

    def select_action(self, training, verbose):
        action = torch.multinomial(self.mask, 1).item()
        return action
