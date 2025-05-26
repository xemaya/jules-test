import unittest
from texas_holdem.core.card import Card
from texas_holdem.core.deck import Deck
from texas_holdem.core.game import Game
from texas_holdem.ai.player import AIPlayer, Player
from texas_holdem.core.hand_evaluator import RANK_VALUES, HAND_RANKS

def create_hand_from_tuples(card_tuples): # Helper
    return [Card(s, r) for s, r in card_tuples]

class TestGame(unittest.TestCase):
    def setUp(self):
        # Setup players for game tests
        self.player1 = AIPlayer(name="P1", chips=1000)
        self.player2 = AIPlayer(name="P2", chips=1000)
        self.players = [self.player1, self.player2]
        self.game = Game(self.players)

    def test_determine_best_hand_royal_flush(self):
        # Player 1 gets hole cards for a Royal Flush with community cards
        self.player1.hand = create_hand_from_tuples([("Hearts", "A"), ("Hearts", "K")])
        self.game.community_cards = create_hand_from_tuples([
            ("Hearts", "Q"), ("Hearts", "J"), ("Hearts", "10"), ("Spades", "2"), ("Clubs", "3")
        ])
        
        name, rank_val, kickers = self.game._determine_best_hand(self.player1)
        self.assertEqual(name, "Royal Flush")
        self.assertEqual(rank_val, HAND_RANKS["Royal Flush"])
        self.assertEqual(kickers, [RANK_VALUES[r] for r in ["A", "K", "Q", "J", "10"]])

    def test_determine_best_hand_full_house_from_community(self):
        # Player has a pair, community makes a higher full house available
        self.player1.hand = create_hand_from_tuples([("Diamonds", "7"), ("Clubs", "7")]) # Pair of 7s
        self.game.community_cards = create_hand_from_tuples([
            ("Hearts", "K"), ("Spades", "K"), ("Diamonds", "K"), # Three Kings
            ("Hearts", "Q"), ("Spades", "J") # Q, J
        ])
        # Best hand should be KKK QQ (using one Q from community and one K from player's view, but best is KKK QJ if player has no Q)
        # Actually, player's 7s don't play if community has KKKQJ.
        # Let's make it so player's cards *do* play.
        # Player has K, 7. Community K, K, Q, Q, J. Player uses K for KKKQQ.
        self.player1.hand = create_hand_from_tuples([("Diamonds", "K"), ("Clubs", "7")])
        self.game.community_cards = create_hand_from_tuples([
            ("Hearts", "K"), ("Spades", "K"), # Two more Kings for Quads if we had another K
            ("Hearts", "Q"), ("Spades", "Q"), ("Diamonds", "J") # Pair of Queens
        ])
        # Player hole: K_D, 7_C
        # Community: K_H, K_S, Q_H, Q_S, J_D
        # Best 5-card hand: K_D, K_H, K_S, Q_H, Q_S (Kings full of Queens)
        
        name, rank_val, kickers = self.game._determine_best_hand(self.player1)
        self.assertEqual(name, "Full House")
        # Expected: K,K,K,Q,Q
        self.assertEqual(kickers, [RANK_VALUES["K"]]*3 + [RANK_VALUES["Q"]]*2)

    # More tests can be added for game progression, betting rounds (though harder to unit test fully),
    # and showdown with multiple players. For now, focusing on _determine_best_hand is a good start.

if __name__ == '__main__':
    unittest.main()
```
