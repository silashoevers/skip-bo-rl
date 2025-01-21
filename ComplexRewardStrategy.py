class ComplexRewardStrategy:
    def __init__(self):
        self.player = None

    def register_player(self, player):
        self.player = player

    def reward_hand_to_discard(self, card_face, discard_index):
        reward = -0.2
        self.player.play_hand_to_discard(card_face, discard_index)
        # TODO write rewards
        return reward

    def reward_discard_to_build(self, discard_index, build_index):
        reward = 0.3
        self.player.play_discard_to_build(discard_index,build_index)
        # TODO write rewards
        return reward

    def reward_hand_to_build(self, card_face, build_index):
        reward = 0.3
        self.player.play_hand_to_build(card_face, build_index)
        # TODO write rewards
        return reward

    def reward_stock_to_build(self, build_index):
        reward = 0.7
        self.player.play_stock_to_build(build_index)
        if len(self.player.stock_pile) < 1:
            reward += 100
        #TODO write rewards
        return reward

    def __str__(self):
        return "complex_computer_player"