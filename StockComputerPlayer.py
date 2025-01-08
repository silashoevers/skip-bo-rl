from ComputerPlayer import ComputerPlayer


class StockComputerPlayer(ComputerPlayer):
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
        reward = 0
        self.play_stock_to_build(build_index)
        reward = 1
        return reward

    def __str__(self):
        return "stock_computer_player"
