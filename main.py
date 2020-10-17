from collections import Counter

import pydealer


class BColors:
    PINK = '\033[95m'
    MAGENTA = '\033[35m'
    HEADER = '\033[95m'
    ORANGE = '\033[33m'
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
    def two_three_of_a_kind(cards, victory_cards):
        victory_cards.empty()
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
                    if not set(three_of_a_kinds.keys()) == set(two_of_a_kinds.keys()):
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
                victory_cards.add(card)
        return can_go_down


class Opponent:
    def __init__(self, name, color):
        self.name = name
        self.hand = pydealer.Stack()
        self.color = color
        self.victory_cards = pydealer.Stack()
        self.down_cards = pydealer.Stack()
        self.formatted_name = f"{self.color}{self.name}{BColors.END_COLOR}"


def prompt_to_choose_card(msg, cards, skip_wilds=False):
    color_format_print_cards(cards, with_indices=True, skip_wilds=skip_wilds)
    return input(msg)


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
    print(get_formatted_card_string(card, index=index))


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


def get_points(cards):
    card_points = 0
    for card in cards:
        if card.value == '2':
            card_points += 20
        elif card.value == 'Ace':
            card_points += 15
        elif card.value == 'Jack' or card.value == 'Queen' or card.value == 'King':
            card_points += 10
        else:
            card_points += int(card.value)
    return card_points


def get_discard_choices(count, opponent):
    possible_discard_choices = []
    for card_index, card in enumerate(opponent.hand):
        if card.value != '2':
            card_count = count.get(card.value)
            if card_count:
                if card_count == 1:
                    possible_discard_choices.append(card_index)
    return possible_discard_choices


def auto_select_down_cards(hand, victory_cards, down_cards):
    for card in list(hand.cards):
        if card in victory_cards.cards:
            down_cards.add(card)
            hand.cards.remove(card)


class Game:
    def __init__(self):
        self.playing = True

        self.verbose = False

        self.deck = pydealer.Deck(rebuild=True) + pydealer.Deck(rebuild=True)
        self.deck.shuffle()

        self.hand = self.deck.deal(11)
        self.hand.sort()

        self.victory_cards = pydealer.Stack()
        self.victory_card_values = set([card.value for card in self.victory_cards.cards])

        self.down = False
        self.down_cards = pydealer.Stack()

        self.opponents = [Opponent("Blinky", color=BColors.RED),
                          Opponent("Pinky", color=BColors.PINK),
                          Opponent("Inky", color=BColors.OK_BLUE),
                          Opponent("Clyde", color=BColors.ORANGE)]

        for opponent in self.opponents:
            opponent.hand = self.deck.deal(11)
            opponent.hand.sort()

        self.discard_pile = pydealer.Stack()
        self.discard_pile.add(self.deck.deal())

        self.round = 1
        self.rounds = {
            1: {"name": "2 x 3 of a kind (No 'May I' allowed on this hand!)",
                "func": VictoryConditions.two_three_of_a_kind},
            2: {"name": "1 x 3 of a kind & 1 x 4 card sequence", "func": None},
            3: {"name": "2 x 4 card sequence", "func": None},
            4: {"name": "3 x 3 of a kind", "func": None},
            5: {"name": "2 x 3 of a kind & 1 x 4 card sequence", "func": None},
            6: {"name": "1 x 3 of a kind & 2 x 4 card sequence", "func": None},
            7: {"name": "3 x 4 card sequence", "func": None}
        }

    def start(self):
        print("===== MAY I? =====\n")
        print(f"Round {self.round}: {self.rounds[self.round]['name']}\n")
        self.current_situation()

        while self.playing:
            if self.rounds[self.round]['func'](self.hand.cards, self.victory_cards) and not self.down:
                self.prompt_for_card_draw()
                self.prompt_to_go_down()
                self.prompt_for_discard()
            else:
                self.prompt_for_card_draw()
                if self.rounds[self.round]['func'](self.hand.cards, self.victory_cards) and not self.down:
                    self.prompt_to_go_down()
                    self.prompt_for_discard()
                else:
                    self.prompt_for_discard()
            for opponent_index, opponent in enumerate(self.opponents, start=1):
                self.opponents_turn(opponent_index, opponent)
                if len(opponent.hand) == 0:
                    print(f"{opponent.formatted_name} has won.")
            self.current_situation()
            if len(self.hand) == 0:
                print("Congratulations, you win :)")
                self.playing = False

    def opponents_turn(self, opponent_index, opponent):

        top_discarded_card = self.discard_pile[len(self.discard_pile) - 1]
        print(f"\n{opponent.formatted_name}'s (opponent #{opponent_index}) turn:")

        # choosing a card

        opponent_card_values = [card.value for card in opponent.hand.cards]
        count = Counter(opponent_card_values)
        take_from_discard_pile = False
        top_discard_match_count = count.get(top_discarded_card.value)
        if top_discarded_card.value in opponent_card_values:
            # depends on the playing style of the AI, but a different playing style could choose to only take
            # the discard if they have one or more of the cards already, or two or more, etc.
            if top_discard_match_count >= 1:
                take_from_discard_pile = True
        if take_from_discard_pile:
            print(f"{opponent.formatted_name}"
                  f" chooses the "
                  f"{get_formatted_card_string(top_discarded_card, index=None)}"
                  f" from the discard pile.")
            opponent.hand.add(self.discard_pile.deal())
            opponent_card_values = [card.value for card in opponent.hand.cards]
            count = Counter(opponent_card_values)
        else:
            print(f"{opponent.formatted_name} chooses a card from the deck.")
            opponent.hand.add(self.deck.deal())
            opponent_card_values = [card.value for card in opponent.hand.cards]
            count = Counter(opponent_card_values)
        # TODO: Improve AI discard selection.

        # check victory condition, and go down if possible

        if self.rounds[self.round]['func'](opponent.hand.cards, opponent.victory_cards):
            if self.round == 1:
                # 2 x 3 of a kind
                opponent.victory_card_values = set([card.value for card in opponent.victory_cards.cards])
                if 1 <= len(opponent.victory_card_values) <= 2 or len(opponent.victory_cards) == 6:
                    print(f"{opponent.formatted_name} is going down.\n")
                    print(f"{opponent.formatted_name} uses the following cards to go down:\n"
                          f"{opponent.victory_cards}")
                    auto_select_down_cards(opponent.hand, opponent.victory_cards, opponent.down_cards)
                    self.down = True

                # TODO: Implement other go down scenarios.

        # discard
        possible_discard_choices = get_discard_choices(count, opponent)
        if possible_discard_choices:
            discarded_card_index = max(possible_discard_choices)
        else:
            # TODO: discarding the largest card in your hand arbitrarily is a really dumb move. fix it
            discarded_card_index = len(opponent.hand.cards) - 1
        discarded_card = self.discard(discarded_card_index, opponent.hand)
        print(f"{opponent.formatted_name} discards: {get_formatted_card_string(discarded_card, index=None)}.")
        input()

    def current_situation(self):
        print(f"Your hand ({get_points(self.hand)} points):\n")
        color_format_print_cards(self.hand)
        if self.down_cards:
            print(f"\nYour down cards:\n")
            color_format_print_cards(self.down_cards)
        if self.verbose:
            print(f"\nDiscard pile (bottom to top):\n{self.discard_pile}\n")
        else:
            print(
                f"\nDiscard pile:\n"
                f"{get_formatted_card_string(self.discard_pile[len(self.discard_pile) - 1], index=None)}\n")

    def prompt_to_go_down(self):
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
            print(f"{BColors.WARNING}Invalid entry. Please try again.{BColors.END_COLOR}\n")

    def go_down(self):
        if self.round == 1:
            # 2 x 3 of a kind
            self.victory_card_values = set([card.value for card in self.victory_cards.cards])
            if 1 <= len(self.victory_card_values) <= 2 or len(self.victory_cards) == 6:
                print("Auto-selecting down cards.")
                auto_select_down_cards(self.hand, self.victory_cards, self.down_cards)
                self.down = True
            else:
                # TODO: Fix choosing of down cards.
                card_groups_needed_to_go_down = 2
                victory_cards_and_values = [(card, card.value) for card in self.victory_cards.cards]
                values = set(map(lambda x: x[1], victory_cards_and_values))
                grouped_victory_cards = sorted([[y[0] for y in victory_cards_and_values if y[1] == x] for x in values])
                for index, card_group in enumerate(grouped_victory_cards):
                    grouped_victory_card_names = [card.name for card in card_group]
                    if '2' in grouped_victory_card_names:
                        # TODO: Wild card condition does not seem to be working - investigate.
                        print(
                            f"X: [{', '.join(map(str, grouped_victory_card_names))}] (Wild cards, not yet selectable)")
                    else:
                        print(f"{index}: [{', '.join(map(str, grouped_victory_card_names))}]")
                    # print(f"{index}: {}")
                for i in range(card_groups_needed_to_go_down):
                    card_set_index = input(f"Choose a set of cards with which to go down."
                                           f"(Set {i + 1} of {card_groups_needed_to_go_down})\n")
                    for card in list(self.hand.cards):
                        if card in grouped_victory_cards[int(card_set_index)]:
                            self.down_cards.add(card)
                            self.hand.cards.remove(card)
                if len(self.down_cards) <= 6 and '2' in self.victory_card_values:
                    add_wild_cards = input("Would you like to add your wild card(s) to your down cards?\n"
                                           "1. Yes\n"
                                           "2. No\n")
                    if add_wild_cards == '1':
                        # TODO: Add wild cards to down cards.
                        self.down = True
                    elif add_wild_cards == '2':
                        self.down = True
        self.down = True

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
                print(f"{BColors.WARNING}Invalid entry. Please try again.{BColors.END_COLOR}\n")

    def prompt_for_discard(self):
        while len(self.hand.cards) % 2 == 0:
            print("Discard one card.\n")
            discard_entry = prompt_to_choose_card("\nWhich card will you discard?\n", self.hand)
            if not discard_entry:
                print(f"{BColors.WARNING}Please select a card.{BColors.END_COLOR}\n")
            elif int(discard_entry) not in range(len(self.hand.cards)):
                print(f"{BColors.WARNING}Invalid entry. Please try again.{BColors.END_COLOR}\n")
            else:
                discarded_card = self.discard(discard_entry, self.hand)
                print(f"You discarded: {get_formatted_card_string(discarded_card, index=None)}.\n")
        print(f"Your hand ({get_points(self.hand)} points) (after discarding):\n")
        color_format_print_cards(self.hand)

    def discard(self, discard_index, hand):
        discarded_card = hand.cards[int(discard_index)]
        self.discard_pile.add(discarded_card)
        del hand.cards[int(discard_index)]
        return discarded_card


if __name__ == '__main__':
    game = Game()
    game.start()
