import unittest
from texas_holdem.core.card import Card
from texas_holdem.core.deck import Deck, SUITS, RANKS

class TestCardDeck(unittest.TestCase):
    def test_card_creation(self):
        card = Card("Hearts", "A")
        self.assertEqual(card.suit, "Hearts")
        self.assertEqual(card.rank, "A")
        self.assertEqual(str(card), "A of Hearts")
        self.assertEqual(repr(card), "Card('Hearts', 'A')")

    def test_deck_creation(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 52)
        unique_cards = set()
        for card in deck.cards:
            unique_cards.add(str(card))
        self.assertEqual(len(unique_cards), 52, "Deck should have 52 unique cards")

    def test_deck_shuffle(self):
        deck1 = Deck()
        deck2 = Deck() # Assumes shuffle is called in __init__
        
        # Check if card lists are different (probabilistic, but good enough for a basic check)
        # To make it more deterministic, we could seed random, or compare string representations
        deck1_str = [str(c) for c in deck1.cards]
        # deck2_str = [str(c) for c in deck2.cards] # Not used in assertNotEqual directly
        
        # If the deck is shuffled on creation, deck1 and deck2 will likely be different.
        # The assertion checks if the shuffled deck1 is different from a brand new, ordered deck.
        ordered_deck_str = [str(Card(s, r)) for s in SUITS for r in RANKS]
        # We need to sort both representations if SUITS and RANKS order isn't guaranteed to match Card creation order in Deck
        # However, Deck() populates in a fixed order before shuffle, so this should be fine.
        
        # A key test: a shuffled deck should not be in the original, ordered sequence.
        self.assertNotEqual(deck1_str, ordered_deck_str, "Deck should be shuffled from ordered state")


    def test_deck_deal(self):
        deck = Deck()
        # My Deck.deal() uses self.cards.pop(), which takes from the end of the list.
        # The "top" card for dealing is the last card in the list after __init__ shuffle.
        # To test this, we need to know the card before dealing.
        if not deck.cards: self.fail("Deck is empty after creation, cannot test deal.") # Should not happen
        
        expected_top_card_obj = deck.cards[-1] # Card object at the end of the list
        
        dealt_card = deck.deal()
        
        self.assertIsNotNone(dealt_card, "Dealt card should not be None from a full deck")
        self.assertEqual(str(dealt_card), str(expected_top_card_obj)) # Compare string representations for equality
        self.assertEqual(len(deck.cards), 51)
        
        for _ in range(51): # Deal all remaining cards
            next_dealt_card = deck.deal()
            self.assertIsNotNone(next_dealt_card, "Should be able to deal all 51 remaining cards.")
            
        self.assertEqual(len(deck.cards), 0, "Deck should be empty after dealing 52 cards.")
        self.assertIsNone(deck.deal(), "Dealing from empty deck should return None")

if __name__ == '__main__':
    unittest.main()
