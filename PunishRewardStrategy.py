import ComputerPlayer


class PunishRewardStrategy:
    def __init__(self):
        self.player = None

    def register_player(self, player):
        self.player = player

    def reward_hand_to_discard(self, card_face, discard_index):
        self.player.play_hand_to_discard(card_face, discard_index)
        return ComputerPlayer.DISCARD_REWARD

    def reward_discard_to_build(self, discard_index, build_index):
        self.player.play_discard_to_build(discard_index,build_index)
        return 0

    def reward_hand_to_build(self, card_face, build_index):
        self.player.play_hand_to_build(card_face, build_index)
        return 0

    def reward_stock_to_build(self, build_index):
        reward = 0
        self.player.play_stock_to_build(build_index)
        return reward

    def reward_loss(self):
        return ComputerPlayer.LOSS_REWARD

    def __str__(self):
        return "punish_computer_player"