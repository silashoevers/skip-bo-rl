from abc import ABC, abstractmethod

import torch

HELP_STRING = """The commands are:
discard build [discard_pile_index] [build_pile_index]
stock build [build_pile_index]
hand build [card_face] [build_pile_index]
hand discard [card_face] [discard_pile_index]. Ends your turn.
"""

class Player(ABC):
    def __init__(self, game):
        self.hand = []
        self.discard_piles = [[], [], [], []]
        self.stock_pile = []
        self.game = game

    @abstractmethod
    def play(self):
        pass

    def fill_hand(self):
        while len(self.hand) < 5:
            self.hand.append(self.game.draw_card())

    def is_face_in_hand(self, card_face):
        return card_face in [card.face for card in self.hand]

    def check_hand_to_build(self, card_face, build_index):
        if self.is_face_in_hand(card_face):
            if card_face == 'S':
                return True
            else:
                return card_face == self.game.get_top_of_build_pile(build_index) + 1
        else:
            return False

    def check_hand_to_discard(self, card_face, discard_index):
        return self.is_face_in_hand(card_face)

    def check_discard_to_build(self, discard_index, build_index):
        if len(self.discard_piles[discard_index]) == 0:
            return False
        elif self.discard_piles[discard_index][-1].face == 'S':
            return True
        else:
            return self.discard_piles[discard_index][-1].value == self.game.get_top_of_build_pile(build_index) + 1

    def check_stock_to_build(self, build_index):
        if self.stock_pile[-1].face == 'S':
            return True
        else:
            return self.stock_pile[-1].value == self.game.get_top_of_build_pile(build_index) + 1

    def get_card_from_hand(self, card_face):
        play_card = next(card for card in self.hand if card == card_face)
        self.hand.remove(play_card)
        return play_card

    def play_hand_to_build(self, card_face, build_index):
        play_card = self.get_card_from_hand(card_face)
        build_pile = self.game.building_piles[build_index]
        if play_card.face == 'S':
            play_card.value = self.game.get_top_of_build_pile(build_index) + 1
        build_pile.append(play_card)

        self.game.clear_build_pile_if_full(build_index)

        if len(self.hand) == 0:
            self.fill_hand()

    def play_hand_to_discard(self, card_face, discard_index):
        play_card = self.get_card_from_hand(card_face)
        discard_pile = self.discard_piles[discard_index]
        discard_pile.append(play_card)

    def play_discard_to_build(self, discard_index, build_index):
        discard_pile = self.discard_piles[discard_index]
        card = discard_pile.pop()
        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)

        self.game.clear_build_pile_if_full(build_index)

    def play_stock_to_build(self, build_index):
        card = self.stock_pile.pop()
        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)

        self.game.clear_build_pile_if_full(build_index)


class HumanPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

    def print_game_state(self):
        # TODO: Add opponent game state (Scale up to 3 other players)
        # TODO: Add index indicator for build and discard piles
        # Building pile top cards
        tops_of_build_piles = [self.game.get_top_of_build_pile(pile_index) for pile_index in range(0,4)]
        print("  ".join([f"[{top if top > 0 else '_'}]" for top in tops_of_build_piles]))
        print()
        # Discard piles. Only show top card per pile
        print(f"[{self.stock_pile[-1]}]]  " + " ".join([f"[{self.discard_piles[pile_index][-1] if len(self.discard_piles[pile_index]) > 0 else '_'}]" for pile_index in range(0,4)]))
        print('----------------------')
        # Hand and stock
        print("=E " + " ".join([f"[{card}]" for card in self.hand]) + " Ǝ=")

    def play(self):
        self.fill_hand()
        end_turn = False
        while not end_turn:
            self.print_game_state()
            match input("What's your move? Type 'help' to get an overview of available commands.\n").split():
                case ["discard", "build", discard_pile_index, build_pile_index]:
                    discard_pile_index, build_pile_index = int(discard_pile_index), int(build_pile_index)
                    if self.check_discard_to_build(discard_pile_index, build_pile_index):
                        self.play_discard_to_build(discard_pile_index, build_pile_index)
                    else:
                       print("Move not legal")
                case ["stock", "build", build_pile_index]:
                    build_pile_index = int(build_pile_index)
                    if self.check_stock_to_build(build_pile_index):
                        self.play_stock_to_build(build_pile_index)
                    else:
                        print("Move not legal")
                case ["hand", "build", card_face, build_pile_index]:
                    # TODO Remove str to int transform (Face should be str, value should be int
                    card_face = int(card_face) if card_face.isdigit() else card_face
                    if self.check_hand_to_build(card_face, int(build_pile_index)):
                        self.play_hand_to_build(card_face, int(build_pile_index))
                    else:
                        print("Move not legal")
                case ["hand", "discard", card_face, discard_pile_index]:
                    card_face = int(card_face) if card_face.isdigit() else card_face
                    if self.check_hand_to_discard(card_face, int(discard_pile_index)):
                        self.play_hand_to_discard(card_face, int(discard_pile_index))
                        end_turn = True
                    else:
                        print("Move not legal")
                case _:  # Unknown command
                    print("Invalid input")
                    print(HELP_STRING)
            # Check if the player has won, if so: end the game
            if len(self.stock_pile) < 1:
                print("Your stock pile is empty, congratulations!")
                self.game.is_game_running = False
                return
        return


class ComputerPlayer(Player):
    def __init__(self, game, device):
        super().__init__(game)
        self.mask = torch.empty(
            13 * 4  # For every card to every build pile, so first card 1 to build 0, then card 1 to build 1 etc.
            + 13 * 4  # For every card to every discard pile, so first card 1 to discard 0, then card 1 to discard 1 etc.
            + 4 * 4  # From every discard pile to every build pile, so discard 0 to build 0, then discard 0 to build 1 etc.
            + 4  # From stock pile to every build pile, so first stock to build 0, then stock to build 1
        ).to(device)
        self.device = device
        self.num_piles = 4

    def compute_mask(self):
        for card in range(1, 14):
            for pile in range(4):
                card_face = 'S' if card == 13 else card
                self.mask[self.num_piles * card + pile] = self.check_hand_to_build(card_face, pile)
        offset = 13 * 4
        for card in range(1, 14):
            card_face = 'S' if card == 13 else card
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

    def can_play_from_stock(self, build_index):
        offset = 13 * 4 + 13 * 4 + 4 * 4
        self.mask[offset + build_index] = self.check_stock_to_build(build_index)

    def next_card_in_hand(self, build_index):
        next_card_value = self.game.get_top_of_build_pile(build_index) + 1
        self.mask[self.num_piles * next_card_value + build_index] = self.check_hand_to_build(next_card_value,
                                                                                             build_index)

    def can_play_from_discard(self, build_index):
        offset = 13 * 4 + 13 * 4
        for discard_pile in range(4):
            self.mask[offset + self.num_piles * discard_pile + build_index] = self.check_discard_to_build(
                discard_pile, build_index)

    # Update the mask for every type of action
    def mask_update_hand_to_build(self, card_face, build_index):
        # Check if we have the next card in hand
        self.next_card_in_hand(build_index)
        # Check if we can play any of our discard pile
        self.can_play_from_discard(build_index)
        # Check if we can play from the stock
        self.can_play_from_stock(build_index)

        # Check if we have the same card again for discard and build
        card_face = 13 if card_face == 'S' else card_face
        for build_pile in range(4):
            self.mask[self.num_piles * card_face + build_pile] = self.check_hand_to_build(card_face, build_pile)
        offset = 13 * 4
        self.mask[offset + self.num_piles * card_face:
                  offset + self.num_piles * card_face + self.num_piles] = self.check_hand_to_discard(
            card_face, 0)

    def mask_update_discard_to_build(self, discard_index, build_index):
        # Check if we have the next card for the build pile in hand
        self.next_card_in_hand(build_index)
        # Check if we can play from stock
        self.can_play_from_stock(build_index)
        # Check if we can play from any discard pile to the build pile
        self.can_play_from_discard(build_index)

        # Check if we can play from our discard pile again
        offset = 13 * 4 + 13 * 4
        for build_pile in range(4):
            self.mask[offset + self.num_piles * discard_index + build_pile] = self.check_discard_to_build(
                discard_index, build_pile)

    def mask_update_stock_to_build(self, build_index):
        # Check if we have the next card in hand
        self.next_card_in_hand(build_index)
        # Check if we can play from discard pile to the build pile
        self.can_play_from_discard(build_index)
        # Check if we can play from the stock
        self.can_play_from_stock(build_index)

    def play(self):
        pass
