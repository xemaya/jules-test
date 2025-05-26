import unittest
from texas_holdem.core.card import Card
from texas_holdem.core.hand_evaluator import evaluate_hand, HAND_RANKS, RANK_VALUES

def create_hand(card_tuples):
    return [Card(suit, rank) for suit, rank in card_tuples]

class TestHandEvaluator(unittest.TestCase):
    def test_royal_flush(self):
        hand = create_hand([("Hearts", "A"), ("Hearts", "K"), ("Hearts", "Q"), ("Hearts", "J"), ("Hearts", "10")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Royal Flush")
        self.assertEqual(rank_val, HAND_RANKS["Royal Flush"])
        self.assertEqual(kickers, [RANK_VALUES[r] for r in ["A", "K", "Q", "J", "10"]])

    def test_straight_flush(self):
        hand = create_hand([("Clubs", "9"), ("Clubs", "8"), ("Clubs", "7"), ("Clubs", "6"), ("Clubs", "5")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Straight Flush")
        self.assertEqual(rank_val, HAND_RANKS["Straight Flush"])
        self.assertEqual(kickers, [RANK_VALUES[r] for r in ["9", "8", "7", "6", "5"]])

    def test_ace_low_straight_flush(self):
        hand = create_hand([("Diamonds", "A"), ("Diamonds", "2"), ("Diamonds", "3"), ("Diamonds", "4"), ("Diamonds", "5")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Straight Flush") # Ace-low is still a Straight Flush
        self.assertEqual(rank_val, HAND_RANKS["Straight Flush"])
        # Kickers for A-5 straight flush should be 5,4,3,2,A (Ace as 1 for comparison if needed)
        self.assertEqual(kickers, [RANK_VALUES["5"], RANK_VALUES["4"], RANK_VALUES["3"], RANK_VALUES["2"], RANK_VALUES["A"]])


    def test_four_of_a_kind(self):
        hand = create_hand([("Hearts", "A"), ("Diamonds", "A"), ("Clubs", "A"), ("Spades", "A"), ("Hearts", "K")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Four of a Kind")
        self.assertEqual(rank_val, HAND_RANKS["Four of a Kind"])
        # Expected: 4 Aces, Kicker King
        self.assertEqual(kickers, [RANK_VALUES["A"]]*4 + [RANK_VALUES["K"]])

    def test_full_house(self):
        # Kings full of Jacks
        hand = create_hand([("Hearts", "K"), ("Diamonds", "K"), ("Clubs", "K"), ("Spades", "J"), ("Hearts", "J")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Full House")
        self.assertEqual(rank_val, HAND_RANKS["Full House"])
        self.assertEqual(kickers, [RANK_VALUES["K"]]*3 + [RANK_VALUES["J"]]*2)

    def test_flush(self):
        hand = create_hand([("Spades", "K"), ("Spades", "Q"), ("Spades", "9"), ("Spades", "5"), ("Spades", "2")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Flush")
        self.assertEqual(rank_val, HAND_RANKS["Flush"])
        self.assertEqual(kickers, sorted([RANK_VALUES[r] for r in ["K", "Q", "9", "5", "2"]], reverse=True))

    def test_straight(self):
        hand = create_hand([("Hearts", "10"), ("Diamonds", "9"), ("Clubs", "8"), ("Spades", "7"), ("Hearts", "6")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Straight")
        self.assertEqual(rank_val, HAND_RANKS["Straight"])
        self.assertEqual(kickers, [RANK_VALUES[r] for r in ["10", "9", "8", "7", "6"]])
    
    def test_ace_low_straight(self):
        hand = create_hand([("Hearts", "A"), ("Diamonds", "2"), ("Clubs", "3"), ("Spades", "4"), ("Hearts", "5")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Straight")
        self.assertEqual(rank_val, HAND_RANKS["Straight"])
        self.assertEqual(kickers, [RANK_VALUES["5"], RANK_VALUES["4"], RANK_VALUES["3"], RANK_VALUES["2"], RANK_VALUES["A"]])


    def test_three_of_a_kind(self):
        hand = create_hand([("Hearts", "Q"), ("Diamonds", "Q"), ("Clubs", "Q"), ("Spades", "A"), ("Hearts", "K")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Three of a Kind")
        self.assertEqual(rank_val, HAND_RANKS["Three of a Kind"])
        # Expected: 3 Queens, Kickers Ace, King
        self.assertEqual(kickers, [RANK_VALUES["Q"]]*3 + sorted([RANK_VALUES["A"], RANK_VALUES["K"]], reverse=True))

    def test_two_pair(self):
        # Aces and Kings, kicker Queen
        hand = create_hand([("Hearts", "A"), ("Diamonds", "A"), ("Clubs", "K"), ("Spades", "K"), ("Hearts", "Q")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "Two Pair")
        self.assertEqual(rank_val, HAND_RANKS["Two Pair"])
        self.assertEqual(kickers, [RANK_VALUES["A"]]*2 + [RANK_VALUES["K"]]*2 + [RANK_VALUES["Q"]])

    def test_one_pair(self):
        # Pair of Jacks, Kickers A, K, Q
        hand = create_hand([("Hearts", "J"), ("Diamonds", "J"), ("Clubs", "A"), ("Spades", "K"), ("Hearts", "Q")])
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "One Pair")
        self.assertEqual(rank_val, HAND_RANKS["One Pair"])
        self.assertEqual(kickers, [RANK_VALUES["J"]]*2 + sorted([RANK_VALUES["A"], RANK_VALUES["K"], RANK_VALUES["Q"]], reverse=True))

    def test_high_card(self):
        hand = create_hand([("Hearts", "A"), ("Diamonds", "K"), ("Clubs", "Q"), ("Spades", "J"), ("Hearts", "9")]) # No pair, not flush, not straight
        name, rank_val, kickers = evaluate_hand(hand)
        self.assertEqual(name, "High Card")
        self.assertEqual(rank_val, HAND_RANKS["High Card"])
        self.assertEqual(kickers, sorted([RANK_VALUES[r] for r in ["A", "K", "Q", "J", "9"]], reverse=True))

    # Add more tests, especially for tie-breaking kickers if evaluate_hand supports detailed comparison
    # e.g. Pair of Aces, K,Q,J vs Pair of Aces, K,Q,10

if __name__ == '__main__':
    unittest.main()
```
