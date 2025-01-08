from Player import Player

HELP_STRING = """The commands are:
discard build [discard_pile_index] [build_pile_index]
stock build [build_pile_index]
hand build [card_face] [build_pile_index]
hand discard [card_face] [discard_pile_index]. Ends your turn.
"""

class HumanPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

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
                    # TODO Remove str to int transform (Face should be str, value should be int)
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