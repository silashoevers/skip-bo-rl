from abc import ABC, abstractmethod


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

    def play_stock_to_build(self, build_index):
        card = self.stock_pile.pop()
        build_pile = self.game.building_piles[build_index]
        build_pile.append(card)


class HumanPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

    def print_game_state(self):

        print("The current build top cards are: " + self.game.get_top_of_build_pile(0) +
              "\t" + self.game.get_top_of_build_pile(1) +
              "\t" + self.game.get_top_of_build_pile(2) +
              "\t" + self.game.get_top_of_build_pile(3) +
              "\n")
        print("Your hand contains: ")
        for i in self.hand:
            print(i)

        print("Your discard piles' top cards are: \n")
        for i in range(len(self.discard_piles)):
            if len(self.discard_piles[i])>0:
                print(str(self.discard_piles[i][len(self.discard_piles[i])-1])+" with " +str(len(self.discard_piles[i]))+" cards left" )
            else:
                print("Empty pile")

        print("Your top stock card is: " + str(self.stock_pile[len(self.stock_pile)-1]) +" with " + str(len(self.stock_pile)) +" cards left")

    def ask_next_move(self):
        move = None
        next_move = input("What would you like to do? [play or discard]")
        if next_move == "play":
            discard_pile = None
            next_card = None
            card_location = input("From where would you like to play? [hand, discard, stock]")
            if card_location == "discard":
                discard_pile = input("Which discard pile? [0-3]")
            if card_location == "hand":
                next_card = input("Which card would you like to play? [1-12 or joker]")
            card_dest = input("On which build pile would you like to place the card? [0-3]")
            move = ("play",card_location,next_card,discard_pile,card_dest)
        else:
            discard = input("Which card would you like to discard? [1-12 or joker]")
            pile = input("To which discard pile? [0-3]")
            move = ("discard",discard,pile)

        return move

    def play(self):
        self.fill_hand()
        end_turn = False
        while not end_turn:
            self.print_game_state()
            move = self.ask_next_move()
            legal = False
            #Check if move is legal
            if move[0] == "play":
                if move[1] == "hand":
                    legal = self.check_hand_to_build(move[2], move[4])
                if move[1] == "discard":
                    legal = self.check_discard_to_build(move[3], move[4])
                if move[1] == "stock":
                    legal = self.check_stock_to_build(move[4])
            if move[0] == "discard":
                legal= self.check_hand_to_discard(move[1], move[2])

            # Play the move if legal, otherwise print error and go to top of loop
            if legal:
                if move[0] == "play":
                    if move[1] == "hand":
                        self.play_hand_to_build(move[2], move[4])
                    if move[1] == "discard":
                        self.play_discard_to_build(move[3], move[4])
                    if move[1] == "stock":
                        self.play_stock_to_build(move[4])
                if move[0] == "discard":
                    self.play_hand_to_discard(move[1], move[2])
                    end_turn = True
            else:
                print("Sorry, that is not a legal move")
                continue

            #Check if the player has won, if so: end the game
            if len(self.stock_pile)<1:
                print("Your stock pile is empty, congratulations!")
                self.game.is_game_running = False
                return
        return


class ComputerPlayer(Player):
    def __init__(self, game):
        super().__init__(game)

    def play(self):
        pass
