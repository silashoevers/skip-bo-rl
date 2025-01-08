from ComputerPlayer import ComputerPlayer

class WinOnlyComputerPlayer(ComputerPlayer):
    def reward_hand_to_discard(self, card_face, discard_index):
        self.play_hand_to_discard(card_face, discard_index)
        return 0

    def reward_discard_to_build(self, discard_index, build_index):
        self.play_discard_to_build(discard_index,build_index)
        return 0

    def reward_hand_to_build(self, card_face, build_index):
        self.play_hand_to_build(card_face, build_index)
        return 0

    def reward_stock_to_build(self, build_index):
        reward = 0
        self.play_stock_to_build(build_index)
        if len(self.stock_pile) < 1:
            reward = 1
        return reward

    def __str__(self):
        return "win_only_computer_player"