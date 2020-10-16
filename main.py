import random
from collections import Counter

import pydealer


class BColors:
    HEADER = '\033[95m'
    OK_BLUE = '\033[94m'
    OK_CYAN = '\033[96m'
    OK_GREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END_COLOR = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class VictoryConditions:
    @staticmethod
    def two_three_of_a_kind(cards, victory_cards_stack):
        can_go_down = False
        victory_cards_type_count = {}
        count = Counter([card.value for card in cards])
        wild_cards = {k: v for k, v in count.items() if k == '2'}
        three_of_a_kinds = {k: v for k, v in count.items() if v >= 3 and k != '2'}
        if not wild_cards:
            # two natural three of a kinds
            if len(three_of_a_kinds) >= 2:
                victory_cards_type_count = three_of_a_kinds
                can_go_down = True
        else:
            # cannot have two wild cards and 1 natural, so these are the only cases to account for
            two_of_a_kinds = {k: v for k, v in count.items() if v >= 2 and k != '2'}
            if two_of_a_kinds:
                if three_of_a_kinds:
                    # one natural three of a kind, and one wild with a deuce
                    victory_cards_type_count = {**wild_cards, **two_of_a_kinds, **three_of_a_kinds}
                    can_go_down = True
                elif len(two_of_a_kinds) >= 2 and wild_cards['2'] >= 2:
                    # two wild three of a kinds with deuces
                    victory_cards_type_count = {**wild_cards, **two_of_a_kinds}
                    can_go_down = True
        # however many victory cards there are
        for card in cards:
            if card.value in victory_cards_type_count.keys():
                victory_cards_stack.add(card)
        return can_go_down


class Opponent:
    def __init__(self, name):
        self.name = name
        self.hand = pydealer.Stack()


def prompt_to_choose_card(msg, cards, skip_wilds=False):
    if skip_wilds:
        for index, card in enumerate(cards):
            if card.value != '2':
                color_format_print_single_card(card, index)
    else:
        for index, card in enumerate(cards):
            color_format_print_single_card(card, index)
    entry = input(msg)
    return entry


def color_format_print_cards(cards, with_indices=False, skip_wilds=False):
    for index, card in enumerate(cards):
        if skip_wilds:
            if card.value != '2':
                if not with_indices:
                    color_format_print_single_card(card, index=None)
                else:
                    color_format_print_single_card(card, index)
        else:
            if not with_indices:
                color_format_print_single_card(card, index=None)
            else:
                color_format_print_single_card(card, index)


def color_format_print_single_card(card, index):
    color_formatted_card = get_formatted_card_string(card, index=index)
    print(color_formatted_card)


def get_formatted_card_string(card, index):
    if card.suit == 'Spades':
        color_formatted_card = f"♠ {card}"
    elif card.suit == 'Hearts':
        color_formatted_card = f"{BColors.RED}♥ {card}{BColors.END_COLOR}"
    elif card.suit == 'Diamonds':
        color_formatted_card = f"{BColors.RED}♦ {card}{BColors.END_COLOR}"
    elif card.suit == 'Clubs':
        color_formatted_card = f"♣ {card}"
    else:
        color_formatted_card = f"_ {card}"
    if index is not None:
        color_formatted_card = f"{index}: {color_formatted_card}"
    return color_formatted_card


class Game:
    def __init__(self):

        self.verbose = False

        self.deck = pydealer.Deck()
        self.deck.shuffle()

        self.hand = self.deck.deal(11)
        self.hand.sort()

        self.victory_cards = pydealer.Stack()
        self.victory_card_values = set([card.value for card in self.victory_cards.cards])

        self.down = False
        self.down_cards = pydealer.Stack()

        self.opponents = [Opponent("Inky"), Opponent("Pinky"), Opponent("Blinky")]

        for opponent in self.opponents:
            opponent.hand = self.deck.deal(11)
            opponent.hand.sort()

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
            for opponent in self.opponents:
                self.opponents_turn(opponent)
            self.current_situation()

    def opponents_turn(self, opponent):
        print(f"It is {opponent.name}'s turn.")
        deck_or_discard_pile = random.randint(0, 1)
        if deck_or_discard_pile == 0:
            print(f"{opponent.name} chooses a card from the deck.")
            opponent.hand.add(self.deck.deal())
        elif deck_or_discard_pile == 1:
            print(f"{opponent.name} chooses the {self.discard_pile[len(self.discard_pile) - 1]} from the discard pile.")
            opponent.hand.add(self.discard_pile.deal())
        # TODO: Improve AI discard selection.
        possible_choices = []
        for card_index, card in enumerate(opponent.hand):
            if card.value != '2':
                possible_choices.append(card_index)
        discarded_card_index = random.choice(possible_choices)
        discarded_card = self.discard(discarded_card_index, opponent.hand)
        print(f"{opponent.name} discards: {get_formatted_card_string(discarded_card, index=None)}.")
        input()

    def current_situation(self):
        print(f"Your hand:\n")
        color_format_print_cards(self.hand)
        if self.verbose:
            print(f"\nDiscard pile (bottom to top):\n{self.discard_pile}\n")
        else:
            print(
                f"\nDiscard pile:\n{get_formatted_card_string(self.discard_pile[len(self.discard_pile) - 1], index=None)}\n")
        if self.down_cards:
            print(f"Your down cards:\n{self.down_cards}")

    def prompt_to_go_down(self):
        self.victory_card_values = set([card.value for card in self.victory_cards.cards])
        print(f"{BColors.OK_BLUE}You may go down using a subset of the following cards:{BColors.END_COLOR}\n")
        color_format_print_cards(self.victory_cards.cards)
        go_down_response = input(f"\n{BColors.OK_CYAN}Will you go down?{BColors.END_COLOR}\n"
                                 "1. Yes\n"
                                 "2. No\n")
        if go_down_response == '1':
            self.go_down()
        elif go_down_response == '2':
            self.down = False
        else:
            print(f"{BColors.WARNING}Invalid entry.{BColors.END_COLOR}\n")

    def go_down(self):
        if self.round == 1:
            # 2 x 3 of a kind
            if 1 <= len(self.victory_card_values) <= 2:
                print("Auto-selecting down cards.")
                self.auto_select_down_cards()
            else:
                cards_to_use_to_go_down = prompt_to_choose_card("Which cards will you use to go down?\n",
                                                                self.victory_cards, skip_wilds=True)
                self.down_cards.add(cards_to_use_to_go_down)
                for down_card_index in cards_to_use_to_go_down:
                    del self.hand.cards[(int(down_card_index))]
        self.down = True

    def auto_select_down_cards(self):
        for card in list(self.hand.cards):
            if card in self.victory_cards.cards:
                self.down_cards.add(card)
                self.hand.cards.remove(card)

    def prompt_for_card_draw(self):
        while len(self.hand.cards) % 2 != 0:
            card_to_draw = input("Will you draw a card from:\n"
                                 "1. The deck?\n"
                                 "2. The discard pile?\n")
            if card_to_draw == '1':
                new_card_stack = self.deck.deal()
                new_card = new_card_stack.cards[len(new_card_stack.cards) - 1]
                print(f"\nYou picked up: {get_formatted_card_string(new_card, index=None)} from the deck.\n")
                self.hand.add(new_card_stack)
                self.hand.sort()
            elif card_to_draw == '2':
                new_card_stack = self.discard_pile.deal()
                new_card = new_card_stack.cards[len(new_card_stack.cards) - 1]
                print(f"You picked up: {get_formatted_card_string(new_card, index=None)} from the discard pile.\n")
                self.hand.add(new_card_stack)
                self.hand.sort()
            else:
                print("Invalid entry.\n")

    def prompt_for_discard(self):
        while len(self.hand.cards) % 2 == 0:
            print("Discard one card.\n")
            discard_entry = prompt_to_choose_card("Which card will you discard?\n", self.hand)

            if not discard_entry:
                print(f"{BColors.WARNING}Empty entry. Please try again.{BColors.END_COLOR}\n")
            elif int(discard_entry) not in range(len(self.hand.cards)):
                print(f"{BColors.WARNING}Invalid entry. Please try again.{BColors.END_COLOR}\n")
            else:
                discarded_card = self.discard(discard_entry, self.hand)
                print(f"You discarded the {discarded_card}.\n")

    def discard(self, discard_index, hand):
        # TODO: Validate entries.
        discarded_card = hand.cards[int(discard_index)]
        self.discard_pile.add(discarded_card)
        del hand.cards[int(discard_index)]
        return discarded_card


if __name__ == '__main__':
    game = Game()
    game.start()
