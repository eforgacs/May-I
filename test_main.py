from collections import deque
from unittest import TestCase
from unittest.mock import patch

import pydealer
from pydealer import Card, Stack

from src.main import VictoryConditions, Game


class TestVictoryConditions(TestCase):
    def setUp(self) -> None:
        self.hand = pydealer.Stack()
        self.victory_cards = pydealer.Stack()

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

    def test_two_three_of_a_kind_non_match(self):
        """Test hands that do not satisfy the victory condition of two three of a kinds."""
        mix = [pydealer.card.Card('3', 'clubs'), pydealer.card.Card('4', 'diamonds'),
               pydealer.card.Card('5', 'hearts'), pydealer.card.Card('6', 'spades')]
        self.hand.add(mix)
        self.assertFalse(VictoryConditions.two_three_of_a_kind(self.hand.cards, self.victory_cards))


class TestGame(TestCase):
    def setUp(self) -> None:
        self.game = Game()
        self.game.hand.empty()
        self.threes_and_fours_hand = Stack(cards=deque(
            [Card(value='3', suit='Clubs'), Card(value='3', suit='Diamonds'), Card(value='3', suit='Hearts'),
             Card(value='4', suit='Clubs'), Card(value='4', suit='Diamonds'), Card(value='4', suit='Hearts')]))

    def test_discard(self):
        all_spades = [pydealer.card.Card('2', 'spades'),
                      pydealer.card.Card('3', 'spades'),
                      pydealer.card.Card('4', 'spades'),
                      pydealer.card.Card('5', 'spades'),
                      pydealer.card.Card('6', 'spades'),
                      pydealer.card.Card('7', 'spades'),
                      pydealer.card.Card('8', 'spades'),
                      pydealer.card.Card('9', 'spades'),
                      pydealer.card.Card('10', 'spades'),
                      pydealer.card.Card('Jack', 'spades'),
                      pydealer.card.Card('Queen', 'spades'),
                      pydealer.card.Card('King', 'spades'),
                      pydealer.card.Card('Ace', 'spades')]
        self.game.hand.add(all_spades)
        self.assertEqual(pydealer.card.Card('Ace', 'spades'), self.game.discard(12, self.game.hand))
        self.assertEqual([pydealer.card.Card('2', 'spades'),
                          pydealer.card.Card('3', 'spades'),
                          pydealer.card.Card('4', 'spades'),
                          pydealer.card.Card('5', 'spades'),
                          pydealer.card.Card('6', 'spades'),
                          pydealer.card.Card('7', 'spades'),
                          pydealer.card.Card('8', 'spades'),
                          pydealer.card.Card('9', 'spades'),
                          pydealer.card.Card('10', 'spades'),
                          pydealer.card.Card('Jack', 'spades'),
                          pydealer.card.Card('Queen', 'spades'),
                          pydealer.card.Card('King', 'spades')], self.game.hand)

    def test_auto_select_down_cards_two_threes(self):
        # Round 1: 2 x 3 of a kind
        threes = [pydealer.card.Card('3', 'clubs'), pydealer.card.Card('3', 'diamonds'),
                  pydealer.card.Card('3', 'hearts')]
        self.game.hand.add(threes)
        fours = [pydealer.card.Card('4', 'clubs'), pydealer.card.Card('4', 'diamonds'),
                 pydealer.card.Card('4', 'hearts')]
        self.game.hand.add(fours)

        self.assertEqual(Stack(), self.game.down_cards)
        self.assertEqual(self.threes_and_fours_hand, self.game.hand)
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        self.game.auto_select_down_cards()

        self.assertEqual(self.threes_and_fours_hand, self.game.down_cards)
        self.assertEqual(Stack(), self.game.hand)

    @patch('builtins.input', return_value='2')
    def test_prompt_to_go_down(self, mock_input):
        self.game.down = True
        self.game.prompt_to_go_down()
        self.assertEqual(False, self.game.down)

    # def test_go_down_auto_select(self):
    #     self.game.hand.add(self.threes_and_fours_hand)
    #     VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
    #     self.game.go_down()
    #     self.assertEqual(Stack(), self.game.hand)
    #     self.assertEqual(self.threes_and_fours_hand, self.game.down_cards)

    # def test_go_down_manual_select(self):
    #     threes = [pydealer.card.Card('3', 'clubs'), pydealer.card.Card('3', 'diamonds'),
    #               pydealer.card.Card('3', 'hearts')]
    #     self.game.hand.add(threes)
    #     fours = [pydealer.card.Card('2', 'clubs'), pydealer.card.Card('4', 'diamonds'),
    #              pydealer.card.Card('4', 'hearts')]
    #     self.game.hand.add(fours)
    #     fives = [pydealer.card.Card('5', 'clubs'), pydealer.card.Card('5', 'diamonds'),
    #               pydealer.card.Card('5', 'hearts')]
    #     self.game.hand.add(fives)
    #     VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
    #     self.game.go_down()
