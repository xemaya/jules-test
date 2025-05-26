from collections import Counter
from typing import List, Tuple, Dict
from .card import Card

# Define constants for hand ranks
HAND_RANKS = {
    "Royal Flush": 10,
    "Straight Flush": 9,
    "Four of a Kind": 8,
    "Full House": 7,
    "Flush": 6,
    "Straight": 5,
    "Three of a Kind": 4,
    "Two Pair": 3,
    "One Pair": 2,
    "High Card": 1
}

# Card rank to numerical value mapping
RANK_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

def get_hand_rank_value(hand_name: str) -> int:
    return HAND_RANKS.get(hand_name, 0)

def sort_cards(cards: List[Card]) -> List[Card]:
    return sorted(cards, key=lambda card: RANK_VALUES[card.rank], reverse=True)

def _get_rank_counts(hand: List[Card]) -> Counter:
    return Counter(RANK_VALUES[card.rank] for card in hand)

def _get_suit_counts(hand: List[Card]) -> Counter:
    return Counter(card.suit for card in hand)

def _is_flush(hand: List[Card]) -> bool:
    suit_counts = _get_suit_counts(hand)
    return len(suit_counts) == 1

def _is_straight(ranks_num: List[int]) -> bool:
    # Ranks_num should be sorted and unique
    if len(ranks_num) != 5: # Should be 5 unique ranks
        return False
    
    # Check for Ace-low straight (A, 2, 3, 4, 5)
    # Ranks_num would be [14, 5, 4, 3, 2] if sorted by RANK_VALUES
    # So, we need to check if the set of ranks is {14, 2, 3, 4, 5}
    if set(ranks_num) == {14, 2, 3, 4, 5}: # Ace, 2, 3, 4, 5
        return True
    
    # Check for general straight
    is_straight_seq = all(ranks_num[i] - ranks_num[i+1] == 1 for i in range(len(ranks_num) - 1))
    return is_straight_seq

def evaluate_hand(hand: List[Card]) -> Tuple[str, int, List[int]]:
    if len(hand) != 5:
        raise ValueError("Hand must contain 5 cards for evaluation.")

    sorted_hand = sort_cards(hand)
    ranks_num_sorted = [RANK_VALUES[c.rank] for c in sorted_hand] # High to low
    unique_ranks_num_sorted = sorted(list(set(ranks_num_sorted)), reverse=True) # e.g. [14, 13, 12, 11, 10] or [14, 5, 4, 3, 2] for Ace-low

    rank_counts = _get_rank_counts(sorted_hand) # Counts of numerical ranks
    
    is_flush_hand = _is_flush(sorted_hand)
    
    # Check for straight:
    # _is_straight needs 5 unique ranks. If not 5 unique ranks, it can't be a straight.
    is_straight_hand = False
    if len(unique_ranks_num_sorted) == 5:
        is_straight_hand = _is_straight(unique_ranks_num_sorted)

    # 1. Royal Flush
    if is_flush_hand and is_straight_hand and ranks_num_sorted == [14, 13, 12, 11, 10]:
        return "Royal Flush", HAND_RANKS["Royal Flush"], ranks_num_sorted

    # 2. Straight Flush
    if is_flush_hand and is_straight_hand:
        # For Ace-low straight flush (A,2,3,4,5 of same suit)
        if set(ranks_num_sorted) == {14, 5, 4, 3, 2}:
            return "Straight Flush", HAND_RANKS["Straight Flush"], [5, 4, 3, 2, 1] # Use 1 for Ace in A-5 straight
        return "Straight Flush", HAND_RANKS["Straight Flush"], ranks_num_sorted

    # 3. Four of a Kind
    for rank_val, count in rank_counts.items():
        if count == 4:
            four_kind_val = rank_val
            kicker = [r for r in ranks_num_sorted if r != four_kind_val][0]
            high_cards = [four_kind_val] * 4 + [kicker]
            return "Four of a Kind", HAND_RANKS["Four of a Kind"], high_cards

    # 4. Full House
    three_kind_val = None
    pair_val = None
    for rank_val, count in rank_counts.items():
        if count == 3:
            three_kind_val = rank_val
        if count == 2:
            pair_val = rank_val
    
    if three_kind_val is not None and pair_val is not None:
        high_cards = [three_kind_val] * 3 + [pair_val] * 2
        return "Full House", HAND_RANKS["Full House"], high_cards

    # 5. Flush
    if is_flush_hand:
        return "Flush", HAND_RANKS["Flush"], ranks_num_sorted # Already sorted high to low

    # 6. Straight
    if is_straight_hand:
        if set(ranks_num_sorted) == {14, 5, 4, 3, 2}: # Ace-low: A,2,3,4,5
            return "Straight", HAND_RANKS["Straight"], [5, 4, 3, 2, 1] # Use 1 for Ace
        return "Straight", HAND_RANKS["Straight"], ranks_num_sorted

    # 7. Three of a Kind
    if three_kind_val is not None: # From Full House check, but no pair_val
        kickers = sorted([r for r in ranks_num_sorted if r != three_kind_val], reverse=True)
        high_cards = [three_kind_val] * 3 + kickers[:2]
        return "Three of a Kind", HAND_RANKS["Three of a Kind"], high_cards

    # 8. Two Pair
    pairs = []
    for rank_val, count in rank_counts.items():
        if count == 2:
            pairs.append(rank_val)
    
    if len(pairs) == 2:
        pairs.sort(reverse=True) # Sort pairs by rank, high to low
        kicker_val = [r for r in ranks_num_sorted if r not in pairs][0]
        high_cards = [pairs[0]]*2 + [pairs[1]]*2 + [kicker_val]
        return "Two Pair", HAND_RANKS["Two Pair"], high_cards

    # 9. One Pair
    if len(pairs) == 1: # From Two Pair check, found only one pair
        pair_val = pairs[0]
        kickers = sorted([r for r in ranks_num_sorted if r != pair_val], reverse=True)
        high_cards = [pair_val]*2 + kickers[:3]
        return "One Pair", HAND_RANKS["One Pair"], high_cards
        
    # 10. High Card
    return "High Card", HAND_RANKS["High Card"], ranks_num_sorted

```
