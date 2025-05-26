import random
from typing import List, Tuple, Dict, Optional 
from ..core.card import Card 

class Player:
    def __init__(self, name: str, chips: int, is_ai: bool = False):
        self.name: str = name
        self.chips: int = chips
        self.hand: List[Card] = []
        self.is_folded: bool = False
        self.current_bet_in_round: int = 0 
        self.is_all_in: bool = False 
        self.is_ai: bool = is_ai 

    def __str__(self) -> str:
        return f"{self.name} ({'AI' if self.is_ai else 'Human'}): {self.chips} chips"

    def reset_for_new_hand(self):
        self.hand = []
        self.is_folded = False
        self.current_bet_in_round = 0
        self.is_all_in = False

    def can_bet(self, total_bet_amount: int) -> bool:
        """
        Checks if the player can make a bet resulting in a total_bet_amount for the round.
        Args:
            total_bet_amount: The total amount the player wishes to have bet in this round.
        """
        chips_to_add = total_bet_amount - self.current_bet_in_round
        return self.chips >= chips_to_add

    def _commit_bet(self, amount_to_add: int) -> int:
        # amount_to_add is the actual additional chips to remove from player's stack for this action
        actual_chips_deducted = min(amount_to_add, self.chips)
        self.chips -= actual_chips_deducted
        self.current_bet_in_round += actual_chips_deducted 
        if self.chips == 0:
            self.is_all_in = True
        return actual_chips_deducted

    def fold(self) -> Tuple[str, int]: 
        self.is_folded = True
        return ("fold", 0)

    def check(self, current_bet_on_table: int) -> Tuple[str, int]:
        if self.current_bet_in_round < current_bet_on_table and not self.is_all_in:
            return self.call(current_bet_on_table)
        return ("check", 0)

    def call(self, current_bet_on_table: int) -> Tuple[str, int]:
        if self.is_all_in: 
            return ("check", 0) 

        amount_needed_to_add = current_bet_on_table - self.current_bet_in_round
        
        if amount_needed_to_add <= 0: 
            return ("check", 0) 

        chips_committed_this_action = self._commit_bet(amount_needed_to_add)
        return ("call", chips_committed_this_action)

    def bet(self, amount: int) -> Tuple[str, int]: # amount is the total intended bet for the round
        if self.is_all_in:
            return ("check", 0) # Already all-in, can't bet more

        # Prompt's logic: "if not self.can_bet(amount) and self.chips > 0: amount = self.chips"
        # Here, `amount` is total bet. `can_bet` checks if `chips >= (amount - current_bet_in_round)`.
        # If player wants to bet `amount` (total) but cannot afford the difference,
        # their bet becomes an all-in. The total all-in amount would be `self.chips + self.current_bet_in_round`.
        chips_required_to_add = amount - self.current_bet_in_round
        
        if self.chips < chips_required_to_add and self.chips > 0 : # Cannot afford the full additional amount, but has some chips
            # This means they go all-in. The new total bet amount becomes their entire stack + what they already put in.
            amount = self.chips + self.current_bet_in_round 
            # Recalculate chips_to_add_to_pot based on this new all-in 'amount'
            chips_to_add_to_pot = amount - self.current_bet_in_round # This should be self.chips
        elif self.chips == 0: # No chips to bet
            return ("check", 0)
        else:
            chips_to_add_to_pot = chips_required_to_add

        if amount <= 0 and self.current_bet_in_round == 0 : # Trying to bet 0 or less as an opening action
             return ("check", 0)
        
        # If chips_to_add_to_pot is not positive, it's not a valid bet/raise.
        if chips_to_add_to_pot <= 0:
            # This can happen if 'amount' (total bet) is <= self.current_bet_in_round
            # This is effectively a check or an invalid bet.
            return ("check", 0)

        action_type = "bet" if self.current_bet_in_round == 0 else "raise"
        
        bet_placed = self._commit_bet(chips_to_add_to_pot)
        
        # If bet_placed is 0 but chips_to_add_to_pot was >0, it means player had no chips. Already handled by self.chips == 0 check.
        # If bet_placed is 0 because chips_to_add_to_pot was 0 or less, already handled.
        
        return (action_type, bet_placed) 

    def get_action(self, game_state: Dict) -> Tuple[str, int]:
        if self.is_all_in: 
            return ("check", 0)

        if not self.is_ai:
            print(f"\nPlayer {self.name}, it's your turn.")
            print(f"  Your hand: {[str(c) for c in self.hand if c is not None]}") 
            print(f"  Your chips: {self.chips}, Your current bet this round: {self.current_bet_in_round}")
            print(f"  Community cards: {[str(c) for c in game_state.get('community_cards', []) if c is not None]}")
            print(f"  Pot size: {game_state.get('pot_size', 0)}")
            current_bet_to_match = game_state.get('current_bet_on_table', 0)
            print(f"  Current bet to match: {current_bet_to_match}")
            
            print(f"  (Player {self.name} is Human - auto-folding for now as per current dev stage)")
            return self.fold() 
        else:
            return self.fold() # Fallback for base Player if accidentally treated as AI


class AIPlayer(Player):
    def __init__(self, name: str, chips: int):
        super().__init__(name, chips, is_ai=True)

    def get_action(self, game_state: Dict) -> Tuple[str, int]:
        if self.is_all_in: 
            return ("check", 0)

        current_bet_on_table = game_state.get("current_bet_on_table", 0)
        big_blind_amount = game_state.get("big_blind_amount", 2) 
        if big_blind_amount <=0: big_blind_amount = 2 # Ensure BB is positive for calculations

        amount_to_call = current_bet_on_table - self.current_bet_in_round
        rand_choice = random.random()

        if amount_to_call > 0: 
            # Player.call and Player.bet methods will handle going all-in if chips are insufficient.
            if rand_choice < 0.3:  
                return self.fold()
            elif rand_choice < 0.8: 
                return self.call(current_bet_on_table)
            else: 
                raise_amount_total_for_round = current_bet_on_table + big_blind_amount
                # Ensure raise is actually increasing the bet beyond current_bet_on_table
                if raise_amount_total_for_round <= current_bet_on_table:
                    raise_amount_total_for_round = current_bet_on_table + big_blind_amount # Default increment
                    if raise_amount_total_for_round <= current_bet_on_table: # If BB was 0 or negative
                         raise_amount_total_for_round = current_bet_on_table + 1 # Absolute minimum increment
                return self.bet(raise_amount_total_for_round)
        else: 
            if rand_choice < 0.5: 
                return self.check(current_bet_on_table)
            else: 
                bet_total_for_round = big_blind_amount 
                return self.bet(bet_total_for_round)
```
