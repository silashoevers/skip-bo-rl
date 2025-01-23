import ComputerPlayer


class WinStockRewardStrategy:
    def __init__(self):
        self.player = None

    def register_player(self, player):
        self.player = player

    def reward_hand_to_discard(self, card_face, discard_index):
        self.player.play_hand_to_discard(card_face, discard_index)
        return 0

    def reward_discard_to_build(self, discard_index, build_index):
        self.player.play_discard_to_build(discard_index,build_index)
        return 0

    def reward_hand_to_build(self, card_face, build_index):
        self.player.play_hand_to_build(card_face, build_index)
        return 0

    def reward_stock_to_build(self, build_index):
        self.player.play_stock_to_build(build_index)
        reward = ComputerPlayer.STOCK_REWARD
        if len(self.player.stock_pile) < 1:
            reward += ComputerPlayer.WIN_REWARD
        return reward

    def reward_loss(self):
        return 0

    def __str__(self):
        return "win_stock_computer_player"