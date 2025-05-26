class Card:
    """
    Represents a playing card with a suit and rank.
    """
    def __init__(self, suit: str, rank: str):
        """
        Initializes a Card object.

        Args:
            suit: The suit of the card (e.g., "Hearts", "Diamonds", "Clubs", "Spades").
            rank: The rank of the card (e.g., "2", "3", ..., "A").
        """
        if suit not in ["Hearts", "Diamonds", "Clubs", "Spades"]:
            raise ValueError(f"Invalid suit: {suit}")
        if rank not in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
            raise ValueError(f"Invalid rank: {rank}")
        self.suit = suit
        self.rank = rank

    def __str__(self) -> str:
        """
        Returns a string representation of the card (e.g., "Ace of Spades").
        """
        return f"{self.rank} of {self.suit}"

    def __repr__(self) -> str:
        """
        Returns a string that can be used to recreate the Card object.
        """
        return f"Card('{self.suit}', '{self.rank}')"
