import torch

from ComputerPlayer import ComputerPlayer


class RandomComputerPlayer(ComputerPlayer):
    def select_action(self, training, verbose, steps_done):
        action = torch.multinomial(self.mask, 1).item()
        return action
