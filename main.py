import random
from collections import Counter

import pydealer


class VictoryConditions:
    @staticmethod
    def two_three_of_a_kind(cards, victory_cards):
        count = Counter([card.value for card in cards])
        wild_cards = {k: v for k, v in count.items() if k == '2'}
        three_of_a_kinds = {k: v for k, v in count.items() if v >= 3 and k != '2'}
        if not wild_cards:
            victory_cards |= three_of_a_kinds
            return len(three_of_a_kinds) >= 2
        else:
            # cannot have two wild cards and 1 natural, so these are the only cases to account for
            two_of_a_kinds = {k: v for k, v in count.items() if v >= 2 and k != '2'}
            if three_of_a_kinds and two_of_a_kinds and wild_cards:
                # one natural three of a kind, and one wild with a deuce
                victory_cards |= two_of_a_kinds
                victory_cards |= wild_cards
                victory_cards |= three_of_a_kinds
                return two_of_a_kinds and wild_cards and three_of_a_kinds
            elif len(two_of_a_kinds) >= 2 or len(three_of_a_kinds) >= 2:
                # two wild three of a kinds with deuces
                victory_cards |= two_of_a_kinds
                victory_cards |= wild_cards
                return len(two_of_a_kinds) >= 2 and wild_cards['2'] >= 2


class Opponent:
    def __init__(self, name):
        self.name = name
        self.hand = pydealer.Stack()


class Game:
    def __init__(self):
        self.verbose = False

        self.deck = pydealer.Deck()
        self.deck.shuffle()

        self.hand = self.deck.deal(11)
        self.hand.sort()

        self.victory_cards = {}

        self.down = False
        self.down_cards = pydealer.Stack()

        self.opponent_1 = Opponent("Inky")
        self.opponent_2 = Opponent("Pinky")
        self.opponent_1.hand = self.deck.deal(11)
        self.opponent_1.hand.sort()
        self.opponent_2.hand = self.deck.deal(11)
        self.opponent_2.hand.sort()

        self.discard_pile = pydealer.Stack()
        self.discard_pile.add(self.deck.deal())

        self.round = 1
        self.rounds = {
            1: {"name": "2 x 3 of a kind", "func": VictoryConditions.two_three_of_a_kind},
            2: {"name": "1 x 3 of a kind & 1 x 4 card sequence", "func": None},
            3: {"name": "2 x 4 card sequence", "func": None},
            4: {"name": "3 x 3 of a kind", "func": None},
            5: {"name": "2 x 3 of a kind & 1 x 4 card sequence", "func": None},
            6: {"name": "1 x 3 of a kind & 2 x 4 card sequence", "func": None},
            7: {"name": "3 x 4 card sequence", "func": None}
        }

    def start(self):
        print(f"Round {self.round}: {self.rounds[self.round]['name']}\n")
        self.current_situation()

        while not self.down:
            if self.rounds[self.round]['func'](self.hand.cards, self.victory_cards):
                self.prompt_for_card_draw()
                self.prompt_to_go_down()
                self.prompt_for_discard()
            else:
                self.prompt_for_card_draw()
                if self.rounds[self.round]['func'](self.hand.cards, self.victory_cards):
                    self.prompt_to_go_down()
                self.prompt_for_discard()
            self.opponents_turn(self.opponent_1)
            self.opponents_turn(self.opponent_2)
            self.current_situation()

    def opponents_turn(self, opponent):
        print(f"It is {opponent.name}'s turn.")
        # TODO: Allow opponents to choose cards from the discard pile as well.
        print(f"{opponent.name} chooses a card from the deck.")
        opponent.hand.add(self.deck.deal())
        # TODO: Improve AI discard selection.
        discarded_card = self.discard(random.choice(range(len(opponent.hand) - 1)), opponent.hand)
        print(f"{opponent.name} discards: {discarded_card}.")
        input()

    def current_situation(self):
        print(f"Your hand:\n{self.hand}\n")
        if self.verbose:
            print(f"Discard pile (bottom to top):\n{self.discard_pile}\n")
        else:
            print(f"Discard pile:\n{self.discard_pile[len(self.discard_pile) - 1]}\n")

    def prompt_to_go_down(self):
        print("You may go down.\n")
        go_down = input("Will you go down?\n"
                        "1. Yes\n"
                        "2. No\n")
        if go_down == '1':
            if self.round == 1:
                self.down_cards.add(self.victory_cards)
                for card in list(self.hand.cards):
                    if card.value in self.victory_cards.keys():
                        self.hand.cards.remove(card)
            self.down = True
        elif go_down == '2':
            self.down = False
        else:
            print("Invalid entry.\n")

    def prompt_for_card_draw(self):
        card_to_draw = input("Will you draw a card from:\n"
                             "1. The deck?\n"
                             "2. The discard pile?\n")
        if card_to_draw == '1':
            new_card = self.deck.deal()
            print(f"\nYou picked up: {new_card}\n")
            self.hand.add(new_card)
            self.hand.sort()
        elif card_to_draw == '2':
            new_card = self.discard_pile.deal()
            print(f"You picked up: {new_card}\n")
            self.hand.add(new_card)
            self.hand.sort()
        else:
            print("Invalid entry.\n")

    def prompt_for_discard(self):
        print("Discard one card.\n")
        for index, card in enumerate(self.hand):
            print(f"{index}: {card}")
        discard_entry = input("Which card will you discard?\n")
        # TODO: Validate entries.
        # if discard_entry not in range(len(self.hand.cards)):
        #     print("Invalid entry.\n")
        discarded_card = self.discard(discard_entry, self.hand)
        print(f"You discarded the {discarded_card}.\n")

    def discard(self, discard_index, hand):
        discarded_card = hand.cards[int(discard_index)]
        self.discard_pile.add(discarded_card)
        hand.cards.__delitem__(int(discard_index))
        return discarded_card


if __name__ == '__main__':
    game = Game()
    game.start()
