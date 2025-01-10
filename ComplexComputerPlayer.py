from ComputerPlayer import ComputerPlayer

class ComplexComputerPlayer(ComputerPlayer):
    def reward_hand_to_discard(self, card_face, discard_index):
        reward = -0.2
        self.play_hand_to_discard(card_face, discard_index)
        # TODO write rewards
        return reward

    def reward_discard_to_build(self, discard_index, build_index):
        reward = 0.3
        self.play_discard_to_build(discard_index,build_index)
        # TODO write rewards
        return reward

    def reward_hand_to_build(self, card_face, build_index):
        reward = 0.3
        self.play_hand_to_build(card_face, build_index)
        # TODO write rewards
        return reward

    def reward_stock_to_build(self, build_index):
        reward = 0.7
        self.play_stock_to_build(build_index)
        if len(self.stock_pile) < 1:
            reward += 100
        #TODO write rewards
        return reward

    def __str__(self):
        return "complex_computer_player"