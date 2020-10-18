from collections import deque, Counter
from unittest import TestCase
from unittest.mock import patch

from pydealer import Card, Stack, VALUES

from src.main import VictoryConditions, Game, get_points, auto_select_down_cards

all_spades = [Card(value, 'spades') for value in VALUES]


def three_of_a_kind(value):
    """A natural three of a kind, comprised of clubs, diamonds and hearts."""
    return [Card(value, 'clubs'),
            Card(value, 'diamonds'),
            Card(value, 'hearts')]


def wild_three_of_a_kind(value):
    """A wild three of a kind, with a 2 of clubs, and the natural cards of diamonds and hearts."""
    return [Card('2', 'clubs'),
            Card(value, 'diamonds'),
            Card(value, 'hearts')]


class TestVictoryConditions(TestCase):
    def setUp(self) -> None:
        self.game = Game()
        self.game.hand.empty()

    def test_two_three_of_a_kind_empty(self):
        self.assertFalse(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))

    def test_two_three_of_a_kind_both_natural(self):
        """Test two natural three of a kinds."""
        self.game.hand.add(three_of_a_kind(3))
        self.game.hand.add(three_of_a_kind(4))
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))

    def test_two_three_of_a_kind_one_natural_one_wild(self):
        """Test one natural three of a kind, and one wild with a deuce."""
        self.game.hand.add(three_of_a_kind(3))
        self.game.hand.add(wild_three_of_a_kind(4))
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))
        self.game.go_down()
        self.assertEqual(Stack(), self.game.hand)
        self.assertEqual(Stack(cards=deque([Card(value='3', suit='Clubs'),
                                            Card(value='3', suit='Diamonds'),
                                            Card(value='3', suit='Hearts'),

                                            Card(value='2', suit='Clubs'),
                                            Card(value='4', suit='Diamonds'),
                                            Card(value='4', suit='Hearts')])), self.game.down_cards)

    def test_two_three_of_a_kind_two_wild(self):
        """Test two wild three of a kinds with deuces."""
        self.game.hand.add(wild_three_of_a_kind(3))
        self.game.hand.add(wild_three_of_a_kind(4))
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))
        self.game.go_down()
        self.assertEqual(Stack(), self.game.hand)
        self.assertEqual(Stack(cards=deque([Card(value='2', suit='Clubs'),
                                            Card(value='3', suit='Diamonds'),
                                            Card(value='3', suit='Hearts'),

                                            Card(value='2', suit='Clubs'),
                                            Card(value='4', suit='Diamonds'),
                                            Card(value='4', suit='Hearts')])), self.game.down_cards)

    def test_three_three_of_a_kinds_natural_on_two_three_hand(self):
        """Test three natural three of a kinds on the two three of a kind hand."""
        self.game.hand.add(three_of_a_kind(3))
        self.game.hand.add(three_of_a_kind(4))
        self.game.hand.add(three_of_a_kind(5))
        self.assertTrue(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))

    def test_two_three_of_a_kind_non_match(self):
        """Test hands that do not satisfy the victory condition of two three of a kinds."""
        mix = [Card('3', 'clubs'),
               Card('4', 'diamonds'),
               Card('5', 'hearts'),
               Card('6', 'spades')]
        self.game.hand.add(mix)
        self.assertFalse(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))

    def test_two_and_three_of_a_kind_overlap(self):
        """Test interesting case - a hand that produced a bug while running the code.
        The bug had to do with overlapping sets of two/three of a kind."""
        overlap_cards = [Card('2', 'Spades'),
                         Card('4', 'Diamonds'),
                         Card('4', 'Hearts'),
                         Card('4', 'Spades'),
                         Card('6', 'Diamonds'),
                         Card('7', 'Hearts'),
                         Card('8', 'Spades'),
                         Card('9', 'Clubs'),
                         Card('10', 'Hearts'),
                         Card('Jack', 'Hearts'),
                         Card('Ace', 'Hearts'),
                         ]
        self.game.hand.add(overlap_cards)
        self.assertFalse(VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards))


class TestGame(TestCase):
    def setUp(self) -> None:
        self.game = Game()
        self.game.hand.empty()
        self.threes_and_fours_hand = Stack(cards=deque(
            [Card(value='3', suit='Clubs'), Card(value='3', suit='Diamonds'), Card(value='3', suit='Hearts'),
             Card(value='4', suit='Clubs'), Card(value='4', suit='Diamonds'), Card(value='4', suit='Hearts')]))

    def test_discard(self):
        all_spades_minus_ace = [spade for spade in all_spades if spade.value != 'Ace']
        self.game.hand.add(all_spades)
        self.assertEqual(Card('Ace', 'spades'), self.game.discard(12, self.game.hand))
        self.assertEqual(all_spades_minus_ace, self.game.hand)

    def test_auto_select_down_cards_two_threes(self):
        # Round 1: 2 x 3 of a kind
        threes = [Card('3', 'clubs'), Card('3', 'diamonds'),
                  Card('3', 'hearts')]
        self.game.hand.add(threes)
        fours = [Card('4', 'clubs'), Card('4', 'diamonds'),
                 Card('4', 'hearts')]
        self.game.hand.add(fours)

        self.assertEqual(Stack(), self.game.down_cards)
        self.assertEqual(self.threes_and_fours_hand, self.game.hand)
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        auto_select_down_cards(self.game.hand, self.game.victory_cards, self.game.down_cards)

        self.assertEqual(self.threes_and_fours_hand, self.game.down_cards)
        self.assertEqual(Stack(), self.game.hand)

    @patch('builtins.input', side_effect='2')
    def test_prompt_to_go_down(self, mock_input):
        self.game.down = True
        self.game.prompt_to_go_down()
        self.assertEqual(False, self.game.down)

    def test_go_down_auto_select(self):
        self.game.hand.add(self.threes_and_fours_hand)
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        self.game.go_down()
        self.assertEqual(Stack(), self.game.hand)
        self.assertEqual(self.threes_and_fours_hand, self.game.down_cards)

    @patch('builtins.input', side_effect=['0', '1'])
    def test_go_down_manual_select(self, mock_input):
        self.game.hand.add(three_of_a_kind(3))
        self.game.hand.add(three_of_a_kind(4))
        self.game.hand.add(three_of_a_kind(5))
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        self.game.go_down()
        self.assertEqual(three_of_a_kind(5), self.game.hand)

    @patch('builtins.input', side_effect=['1', '2'])
    def test_go_down_manual_select2(self, mock_input):
        self.game.hand.add(three_of_a_kind(3))
        self.game.hand.add(three_of_a_kind(4))
        self.game.hand.add(three_of_a_kind(5))
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        self.game.go_down()
        self.assertEqual(three_of_a_kind(3), self.game.hand)

    @patch('builtins.input', side_effect=['1', '2', '1'])
    def test_go_down_manual_select_with_wild_cards(self, mock_input):
        self.game.hand.add(wild_three_of_a_kind(3))
        self.game.hand.add(wild_three_of_a_kind(4))
        self.game.hand.add(wild_three_of_a_kind(5))
        VictoryConditions.two_three_of_a_kind(self.game.hand.cards, self.game.victory_cards)
        self.game.go_down()
        self.assertEqual(Stack(cards=deque([Card(value='5', suit='Diamonds'), Card(value='5', suit='Hearts')])),
                         self.game.hand)

    def test_get_points_of_hand_JQK(self):
        self.game.hand.add(Card("Jack", "Clubs"))
        self.assertEqual(10, get_points(self.game.hand))
        self.game.hand.add(Card("Queen", "Clubs"))
        self.assertEqual(20, get_points(self.game.hand))
        self.game.hand.add(Card("King", "Clubs"))
        self.assertEqual(30, get_points(self.game.hand))

    def test_get_points_of_hand_Ace(self):
        self.game.hand.add(Card("Ace", "Clubs"))
        self.assertEqual(15, get_points(self.game.hand))

    def test_get_points_of_hand_2(self):
        self.game.hand.add(Card("2", "Clubs"))
        self.assertEqual(20, get_points(self.game.hand))

    def test_get_points_of_hand_all_spades(self):
        self.game.hand.add(all_spades)
        self.assertEqual(117, get_points(self.game.hand))

    @patch('builtins.input', side_effect='1')
    def test_prompt_to_meld_auto_meld(self, mock_input):
        self.game.hand.add(all_spades)
        self.game.down = True

        self.game.opponents[0].down_cards.add(three_of_a_kind(3))
        self.game.opponents[0].down_cards.add(three_of_a_kind(4))

        self.game.opponents[1].down_cards.add(three_of_a_kind(4))
        self.game.opponents[1].down_cards.add(three_of_a_kind(5))

        self.game.opponents[2].down_cards.add(three_of_a_kind(5))
        self.game.opponents[2].down_cards.add(three_of_a_kind(6))
        self.game.prompt_to_meld()
        self.assertEqual(deque([Card(value='2', suit='Spades'),
                                Card(value='7', suit='Spades'),
                                Card(value='8', suit='Spades'),
                                Card(value='9', suit='Spades'),
                                Card(value='10', suit='Spades'),
                                Card(value='Jack', suit='Spades'),
                                Card(value='Queen', suit='Spades'),
                                Card(value='King', suit='Spades'),
                                Card(value='Ace', suit='Spades')]), self.game.hand.cards)

    @patch('builtins.input', side_effect=['2', '1', '1', '1', '1'])
    def test_prompt_to_meld_manual_meld(self, mock_input):
        self.game.hand.add(all_spades)
        self.game.down = True

        self.game.opponents[0].down_cards.add(three_of_a_kind(3))
        self.game.opponents[0].down_cards.add(three_of_a_kind(4))

        self.game.opponents[1].down_cards.add(three_of_a_kind(4))
        self.game.opponents[1].down_cards.add(three_of_a_kind(5))

        self.game.opponents[2].down_cards.add(three_of_a_kind(5))
        self.game.opponents[2].down_cards.add(three_of_a_kind(6))
        self.game.prompt_to_meld()
        self.assertEqual(deque([Card(value='2', suit='Spades'),
                                Card(value='7', suit='Spades'),
                                Card(value='8', suit='Spades'),
                                Card(value='9', suit='Spades'),
                                Card(value='10', suit='Spades'),
                                Card(value='Jack', suit='Spades'),
                                Card(value='Queen', suit='Spades'),
                                Card(value='King', suit='Spades'),
                                Card(value='Ace', suit='Spades')]), self.game.hand.cards)

    def test_get_discard_choices(self):
        self.game.hand.add(all_spades)
        self.game.down = True
        for opponent in self.game.opponents:
            opponent.hand.empty()

        self.game.opponents[0].hand.add(all_spades)
        self.game.opponents[0].down_cards.add(three_of_a_kind(3))
        self.game.opponents[0].down_cards.add(three_of_a_kind(4))

        self.game.opponents[1].down_cards.add(three_of_a_kind(4))
        self.game.opponents[1].down_cards.add(three_of_a_kind(5))

        self.game.opponents[2].down_cards.add(three_of_a_kind(5))
        self.game.opponents[2].down_cards.add(three_of_a_kind(6))

        # 7 of Spades through Ace of Spades (indices)
        self.assertEqual([5, 6, 7, 8, 9, 10, 11, 12], self.game.get_discard_choices(self.game.opponents[0]))
