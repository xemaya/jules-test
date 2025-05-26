import random
from .card import Card

SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

class Deck:
    """
    Represents a deck of 52 playing cards.
    """
    def __init__(self):
        """
        Initializes a Deck object, populates it with 52 cards, and shuffles them.
        """
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        """
        Shuffles the cards in the deck.
        """
        random.shuffle(self.cards)

    def deal(self) -> Card | None:
        """
        Removes and returns the top card from the deck.
        Returns None if the deck is empty.
        """
        if not self.cards:
            return None
        return self.cards.pop()

    def __len__(self) -> int:
        """
        Returns the number of cards currently in the deck.
        """
        return len(self.cards)

    def __str__(self) -> str:
        """
        Returns a string indicating the number of cards remaining in the deck.
        """
        return f"Deck with {len(self.cards)} cards remaining."
