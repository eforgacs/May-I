from collections import Counter

import pydealer

rounds = {
    1: "2 x 3 of a kind",
    2: "1 x 3 of a kind & 1 x 4 card sequence",
    3: "2 x 4 card sequence",
    4: "3 x 3 of a kind",
    5: "2 x 3 of a kind & 1 x 4 card sequence",
    6: "1 x 3 of a kind & 2 x 4 card sequence",
    7: "3 x 4 card sequence"
}


def two_three_of_a_kind(values):
    wild_card_count = values['2']
    three_of_a_kind_count = len([i for i in list(values.values()) if i >= 3])
    if not wild_card_count:
        return three_of_a_kind_count >= 2
    else:
        # cannot have two wild cards and 1 natural, so this is the only case to account for
        two_of_a_kind_count = len([i for i in list(values.values()) if i >= 2])
        return (two_of_a_kind_count >= 2 and wild_card_count >= 2) or \
               (two_of_a_kind_count >= 1 and wild_card_count >= 1 and three_of_a_kind_count >= 1)


class Game:
    def __init__(self):
        self.deck = pydealer.Deck()
        self.deck.shuffle()
        self.hand = self.deck.deal(11)
        self.hand.sort()
        self.opponents_hand = self.deck.deal(11)
        self.opponents_hand.sort()
        self.down = False
        self.discard_pile = pydealer.Stack()
        self.discard_pile.add(self.deck.deal())
        self.round = 1

    def start(self):
        print(f"Round {self.round}: {rounds[self.round]}\n")

        self.current_situation()

        while not self.down:
            # if two three of a kind
            card_values = []
            for card in self.hand.cards:
                card_values.append(card.value)
            count = Counter(card_values)
            print("\n")
            self.prompt_for_card_draw()
            if two_three_of_a_kind(count):
                self.prompt_to_go_down()
                self.prompt_for_discard()
            else:
                self.prompt_for_discard()
            self.current_situation()

    def current_situation(self):
        print(f"Your hand:\n{self.hand}\n")
        print(f"Discard pile (bottom to top):\n{self.discard_pile}\n")

    def prompt_to_go_down(self):
        print("You may go down.\n")
        go_down = input("Will you go down?\n"
                        "1. Yes\n"
                        "2. No\n")
        if go_down == '1':
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
        # print(self.hand)
        for index, card in enumerate(self.hand):
            print(f"{index}: {card}")
        discard_entry = input("Which card will you discard?\n")
        discarded_card = self.hand.cards[int(discard_entry)]
        self.discard_pile.add(discarded_card)
        self.hand.cards.__delitem__(int(discard_entry))
        print(f"Discarded the {discarded_card}.\n")


if __name__ == '__main__':
    game = Game()
    game.start()
