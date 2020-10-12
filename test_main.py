from unittest import TestCase

import pydealer

from src.main import VictoryConditions


class TestVictoryConditions(TestCase):
    def setUp(self) -> None:
        self.hand = pydealer.Stack()
        self.victory_cards = {}

    def test_two_three_of_a_kind_empty(self):
        self.assertFalse(VictoryConditions.two_three_of_a_kind(self.hand.cards, self.victory_cards))

    def test_two_three_of_a_kind_both_natural(self):
        """Test two natural three of a kinds."""
        threes = [pydealer.card.Card('3', 'clubs'), pydealer.card.Card('3', 'diamonds'),
                  pydealer.card.Card('3', 'hearts')]
        self.hand.add(threes)
        fours = [pydealer.card.Card('4', 'clubs'), pydealer.card.Card('4', 'diamonds'),
                 pydealer.card.Card('4', 'hearts')]
        self.hand.add(fours)
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.hand.cards, self.victory_cards))

    def test_two_three_of_a_kind_one_natural_one_wild(self):
        """Test one natural three of a kind, and one wild with a deuce."""
        threes = [pydealer.card.Card('3', 'clubs'), pydealer.card.Card('3', 'diamonds'),
                  pydealer.card.Card('3', 'hearts')]
        self.hand.add(threes)
        fours = [pydealer.card.Card('2', 'clubs'), pydealer.card.Card('4', 'diamonds'),
                 pydealer.card.Card('4', 'hearts')]
        self.hand.add(fours)
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.hand.cards, self.victory_cards))

    def test_two_three_of_a_kind_two_wild(self):
        """Test two wild three of a kinds with deuces."""
        threes = [pydealer.card.Card('2', 'clubs'), pydealer.card.Card('3', 'diamonds'),
                  pydealer.card.Card('3', 'hearts')]
        self.hand.add(threes)
        fours = [pydealer.card.Card('2', 'clubs'), pydealer.card.Card('4', 'diamonds'),
                 pydealer.card.Card('4', 'hearts')]
        self.hand.add(fours)
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.hand.cards, self.victory_cards))
