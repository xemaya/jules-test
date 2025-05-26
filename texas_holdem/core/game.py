from .deck import Deck
from .card import Card 
from .hand_evaluator import evaluate_hand, RANK_VALUES 
from ..ai.player import Player 
from typing import List, Dict, Tuple, Optional 
import itertools

class Game:
    def __init__(self, players: List[Player], initial_dealer_pos: int = 0):
        self.players: List[Player] = players
        self.deck: Deck = Deck()
        self.community_cards: List[Card] = []
        self.pot: int = 0
        self.current_bet_on_table: int = 0
        self.dealer_pos: int = initial_dealer_pos % len(self.players) if self.players else 0
        self._small_blind_amount: int = 1 
        self._big_blind_amount: int = 2   
        self._last_raise_amount: int = self._big_blind_amount 
        num_players = len(self.players)
        if num_players == 0: self.current_player_turn: int = 0
        elif num_players == 1: self.current_player_turn: int = self.dealer_pos
        elif num_players == 2: self.current_player_turn: int = self.dealer_pos 
        else: 
            bb_pos = (self.dealer_pos + 2) % num_players
            self.current_player_turn: int = (bb_pos + 1) % num_players
        self._current_round_active_players: List[Player] = []

    def _rotate_dealer(self):
        if not self.players: return
        self.dealer_pos = (self.dealer_pos + 1) % len(self.players)

    def _post_blinds(self): # Verified: Correctly uses player.bet and sets game state.
        if not self.players or len(self.players) == 0: print("No players to post blinds."); return
        num_players = len(self.players)
        sb_player_pos = self.dealer_pos 
        if num_players > 2: sb_player_pos = (self.dealer_pos + 1) % num_players
        
        if num_players >= 1 : 
            sb_player = self.players[sb_player_pos]
            print(f"{sb_player.name} to post small blind of {self._small_blind_amount}.")
            _, sb_amount_committed = sb_player.bet(self._small_blind_amount) 
            self.pot += sb_amount_committed
            print(f"{sb_player.name} posts small blind of {sb_amount_committed}" + (" (all-in)" if sb_player.is_all_in else "") + f". Player chips: {sb_player.chips}")

        if num_players >= 2:
            bb_player_pos = (self.dealer_pos + 1) % num_players 
            if num_players > 2: bb_player_pos = (self.dealer_pos + 2) % num_players
            bb_player = self.players[bb_player_pos]
            print(f"{bb_player.name} to post big blind of {self._big_blind_amount}.")
            _, bb_amount_committed = bb_player.bet(self._big_blind_amount)
            self.pot += bb_amount_committed
            print(f"{bb_player.name} posts big blind of {bb_amount_committed}" + (" (all-in)" if bb_player.is_all_in else "") + f". Player chips: {bb_player.chips}")

            self.current_bet_on_table = bb_player.current_bet_in_round 
            self._last_raise_amount = self._big_blind_amount 

            if num_players == 2: self.current_player_turn = self.dealer_pos
            else: self.current_player_turn = (bb_player_pos + 1) % num_players
        elif num_players == 1: 
            sb_player_ref = self.players[sb_player_pos]
            self.current_bet_on_table = sb_player_ref.current_bet_in_round
            self._last_raise_amount = self._small_blind_amount 
            self.current_player_turn = sb_player_pos
        else: 
             self.current_bet_on_table = 0
             self._last_raise_amount = self._big_blind_amount

    def _deal_hole_cards(self): # Verified: Seems correct.
        print("\n--- Dealing Hole Cards ---")
        if not self.players: return
        start_player_idx = (self.dealer_pos + 1) % len(self.players)
        for i in range(len(self.players) * 2): 
            player_idx = (start_player_idx + i) % len(self.players)
            player = self.players[player_idx]
            if not player.is_folded and len(player.hand) < 2:
                card = self.deck.deal()
                if card: player.hand.append(card)
                else: print("Error: Deck empty dealing hole cards."); return 
        for player in self.players:
            if not player.is_folded: print(f"{player.name} received hole cards.") # Actual cards kept private

    def _deal_flop(self): # Verified: Seems correct.
        if self.deck.deal(): 
            flop_cards = [self.deck.deal(), self.deck.deal(), self.deck.deal()]
            self.community_cards = [c for c in flop_cards if c is not None]
            if len(self.community_cards) == 3:
                 print(f"\n--- Flop --- Community cards: {', '.join(map(str, self.community_cards))}")
            else: print("Error: Could not deal 3 cards for flop.")
        else: print("Error: Deck empty before burning for flop.")

    def _deal_turn_or_river(self, stage_name: str): # Verified: Seems correct.
        if self.deck.deal(): 
            new_card = self.deck.deal()
            if new_card:
                self.community_cards.append(new_card)
                print(f"\n--- {stage_name} --- Community cards: {', '.join(map(str, self.community_cards))}")
            else: print(f"Error: Deck empty dealing {stage_name} card.")
        else: print(f"Error: Deck empty before burning for {stage_name}.")

    def _conduct_betting_round(self, round_name: str):
        print(f"\n--- {round_name} Betting Round ---")
        num_players = len(self.players)
        if num_players == 0: return

        # 1. Initialization for post-flop rounds
        if round_name != "Pre-flop":
            self.current_bet_on_table = 0
            self._last_raise_amount = self._big_blind_amount 
            self.current_player_turn = (self.dealer_pos + 1) % num_players
            # Find first player to act (not folded, not all-in)
            for _ in range(num_players): 
                player = self.players[self.current_player_turn]
                if not player.is_folded and not player.is_all_in: break
                self.current_player_turn = (self.current_player_turn + 1) % num_players
        
        # Determine players who can act this round
        # This list might shrink if players fold.
        # Players who are all-in don't act but are part of showdown.
        
        # player_to_close_action_idx: Player who made the last aggressive action.
        # Action ends when it's their turn again and all other bets are matched.
        # Or, if pre-flop and no raise, it's the BB.
        # Or, if post-flop and no bet, it's the last player in position (e.g. dealer) if all check.
        player_to_close_action_idx = -1
        if round_name == "Pre-flop": # BB is initial reference point
            if num_players > 2: player_to_close_action_idx = (self.dealer_pos + 2) % num_players
            elif num_players == 2: player_to_close_action_idx = (self.dealer_pos + 1) % num_players
        else: # Post-flop, first to act effectively "opens" the betting pass.
              # If a bet occurs, that player becomes player_to_close_action_idx.
              # If all check, it's more nuanced: typically closes on the button or last active player.
              # For simplicity, we'll use the first player to act as the initial reference if no bets.
            player_to_close_action_idx = self.current_player_turn 


        acted_this_bet_level = [False] * num_players # Tracks if player has acted on current bet amount
        
        # Safety break for loop
        actions_this_round_limit = num_players * 4  # Heuristic for max actions
        actions_taken_this_round = 0

        while actions_taken_this_round < actions_this_round_limit:
            actions_taken_this_round += 1

            num_active_not_folded = sum(1 for p in self.players if not p.is_folded)
            if num_active_not_folded <= 1: break # Hand ends or betting unnecessary

            current_player_obj = self.players[self.current_player_turn]
            player_idx = self.current_player_turn

            # Check if betting is settled.
            # All non-folded, non-all-in players must have acted_this_bet_level = True,
            # AND their current_bet_in_round must be == self.current_bet_on_table.
            betting_is_settled = True
            num_players_can_still_act_on_level = 0 # Not folded, not all-in, and needs to act or bet matches
            
            for i in range(num_players):
                p = self.players[i]
                if not p.is_folded and not p.is_all_in:
                    num_players_can_still_act_on_level +=1
                    if not acted_this_bet_level[i] or \
                       (p.current_bet_in_round < self.current_bet_on_table):
                        betting_is_settled = False
                        break 
            
            if num_players_can_still_act_on_level == 0 : # All remaining are all-in
                betting_is_settled = True

            if betting_is_settled:
                print("Betting settled: All active players acted and bets reconciled.")
                break
            
            # Player Turn
            if current_player_obj.is_folded or current_player_obj.is_all_in:
                acted_this_bet_level[player_idx] = True # Cannot act, so considered "acted"
                self.current_player_turn = (self.current_player_turn + 1) % num_players
                continue

            print(f"\nPlayer {current_player_obj.name}'s turn (Chips: {current_player_obj.chips}). Pot: {self.pot}")
            print(f"  Bet to match: {self.current_bet_on_table}. Your current bet: {current_player_obj.current_bet_in_round}.")

            game_state = {
                "community_cards": [str(c) for c in self.community_cards if c], "pot_size": self.pot,
                "current_bet_on_table": self.current_bet_on_table,
                "player_current_bet_in_round": current_player_obj.current_bet_in_round,
                "player_chips": current_player_obj.chips,
                "min_raise_to": self.current_bet_on_table + self._last_raise_amount,
                "big_blind_amount": self._big_blind_amount, "small_blind_amount": self._small_blind_amount,
                "num_active_players": num_active_players_in_hand, # Players not folded
            }

            action_type, amount_for_action = current_player_obj.get_action(game_state)
            acted_this_bet_level[player_idx] = True
            print(f"  {current_player_obj.name} chose: {action_type.upper()}" + (f" {amount_for_action}" if amount_for_action > 0 else ""))

            if action_type == "fold":
                print(f"  {current_player_obj.name} folds.")
                if self._check_hand_over_due_to_folds(is_betting_round_fold=True): break
            elif action_type == "check":
                if current_player_obj.current_bet_in_round < self.current_bet_on_table:
                    print(f"  Illegal Check by {current_player_obj.name}. Auto-folding.")
                    current_player_obj.fold()
                    if self._check_hand_over_due_to_folds(is_betting_round_fold=True): break
                else:
                    print(f"  {current_player_obj.name} checks.")
                    # If no bet on table and this player checks, they become a point of reference for closing action if all check.
                    if self.current_bet_on_table == 0 and player_to_close_action_idx == self.current_player_turn:
                         # This means action checked around to the opener (or BB pre-flop if no bet before them)
                         pass # Loop termination will catch this if all acted_this_bet_level are true
            elif action_type == "call":
                self.pot += amount_for_action 
                print(f"  {current_player_obj.name} calls {amount_for_action}. Pot: {self.pot}.")
                if current_player_obj.is_all_in: print(f"  {current_player_obj.name} is all-in.")
            elif action_type == "bet" or action_type == "raise":
                self.pot += amount_for_action
                previous_bet_on_table = self.current_bet_on_table
                
                if current_player_obj.current_bet_in_round > previous_bet_on_table: 
                    self.current_bet_on_table = current_player_obj.current_bet_in_round
                    actual_raise_amount = self.current_bet_on_table - previous_bet_on_table
                    
                    # Update _last_raise_amount only if it's a "full" raise.
                    # Player.bet() should ensure the total bet amount is valid.
                    # The game needs to ensure the *raise portion* is valid.
                    min_valid_raise_amount = self._last_raise_amount
                    if previous_bet_on_table == 0 : min_valid_raise_amount = self._big_blind_amount

                    if actual_raise_amount >= min_valid_raise_amount or current_player_obj.is_all_in: # All-in for less than full raise is allowed but may not reopen betting fully for some rules
                        self._last_raise_amount = actual_raise_amount # Update with the actual raise amount if it's a "full" raise for future min_raise_to
                    
                    print(f"  {current_player_obj.name} {action_type.upper()}S to {self.current_bet_on_table} (added {amount_for_action}). Pot: {self.pot}.")
                    player_to_close_action_idx = player_idx # New aggressor
                    # Reset acted_this_bet_level for other non-folded, non-all-in players
                    for i in range(num_players):
                        if i != player_idx and not self.players[i].is_folded and not self.players[i].is_all_in:
                            acted_this_bet_level[i] = False
                else: 
                    print(f"  {current_player_obj.name} commits {amount_for_action} (no change to current bet level). Pot: {self.pot}.")
                if current_player_obj.is_all_in: print(f"  {current_player_obj.name} is all-in.")
            
            self.current_player_turn = (self.current_player_turn + 1) % num_players
            if sum(1 for p in self.players if not p.is_folded) <= 1: break 
        
        if actions_this_round_count >= actions_this_round_limit:
            print(f"Warning: Betting round '{round_name}' exceeded action limit. Pot: {self.pot}")
        print(f"--- End of {round_name} Betting Round --- Pot: {self.pot}")

    def _determine_best_hand(self, player: Player) -> Optional[Tuple[str, int, List[int]]]:
        if len(self.community_cards) < 3: return None 
        player_cards = player.hand; all_seven_cards = player_cards + self.community_cards
        if len(all_seven_cards) < 5: return None 
        best_hand_overall = ("High Card", 0, []) 
        for combo_cards_objects in itertools.combinations(all_seven_cards, 5):
            current_combo_list = list(combo_cards_objects)
            if any(c is None for c in current_combo_list): continue 
            hand_name, hand_rank_val, high_card_values = evaluate_hand(current_combo_list)
            if hand_rank_val > best_hand_overall[1]:
                best_hand_overall = (hand_name, hand_rank_val, high_card_values)
            elif hand_rank_val == best_hand_overall[1]:
                for i in range(len(high_card_values)):
                    if high_card_values[i] > best_hand_overall[2][i]:
                        best_hand_overall = (hand_name, hand_rank_val, high_card_values); break
                    if high_card_values[i] < best_hand_overall[2][i]: break 
        return best_hand_overall

    def _showdown(self):
        print("\n--- Showdown ---")
        active_players_at_showdown = [p for p in self._current_round_active_players if not p.is_folded]
        if not active_players_at_showdown: print("No players left for showdown."); return
        if len(active_players_at_showdown) == 1:
            winner = active_players_at_showdown[0]
            print(f"{winner.name} wins the pot of {self.pot} as the only remaining player.")
            winner.chips += self.pot; self.pot = 0; return
        best_hands_for_players: List[Tuple[Player, Tuple[str, int, List[int]]]] = []
        community_card_strs = [str(c) for c in self.community_cards if c]
        print("Community Cards:", ", ".join(community_card_strs))
        for player in active_players_at_showdown:
            player_hole_cards_str = [str(c) for c in player.hand if c]
            player_best_hand_tuple = self._determine_best_hand(player)
            if player_best_hand_tuple:
                best_hands_for_players.append((player, player_best_hand_tuple))
                print(f"{player.name} (Hole: {', '.join(player_hole_cards_str)}) has: {player_best_hand_tuple[0]} (Ranks: {player_best_hand_tuple[2]})")
            else:
                print(f"{player.name} (Hole: {', '.join(player_hole_cards_str)}) could not form a 5-card hand.")
        if not best_hands_for_players: print("No valid hands to compare at showdown."); return
        best_hands_for_players.sort(key=lambda x: (x[1][1], x[1][2]), reverse=True)
        winner_player_obj, winner_hand_info = best_hands_for_players[0]
        winners = [best_hands_for_players[0]]
        for i in range(1, len(best_hands_for_players)):
            if best_hands_for_players[i][1][1] == winner_hand_info[1] and \
               best_hands_for_players[i][1][2] == winner_hand_info[2]:
                winners.append(best_hands_for_players[i])
            else: break 
        if len(winners) > 1:
            pot_per_winner = self.pot // len(winners)
            remainder = self.pot % len(winners) 
            print(f"Split pot of {self.pot} between {len(winners)} players:")
            for p_tuple in winners:
                p_obj = p_tuple[0]; p_obj.chips += pot_per_winner
                print(f"  {p_obj.name} wins {pot_per_winner} with {p_tuple[1][0]} (Ranks: {p_tuple[1][2]})")
            if remainder > 0 and winners:
                 winners[0][0].chips += remainder
                 print(f"  {winners[0][0].name} receives remaining {remainder} chip(s).")
        else: 
            winner_player_obj.chips += self.pot
            print(f"{winner_player_obj.name} wins the pot of {self.pot} with {winner_hand_info[0]} (Ranks: {winner_hand_info[2]}).")
        self.pot = 0

    def play_hand(self):
        print("\n\n--- New Hand Starting ---")
        if not self.players or len(self.players) < 2 :
            print("Not enough players (need at least 2)."); return
        self.deck = Deck(); self.community_cards = []; self.pot = 0
        self._current_round_active_players = []
        for player in self.players:
            player.reset_for_new_hand() 
            if player.chips > 0: self._current_round_active_players.append(player)
        if len(self._current_round_active_players) < 2:
            print("Not enough active players with chips."); return
        self._rotate_dealer()
        print(f"Dealer is {self.players[self.dealer_pos].name}.")
        self._post_blinds() 
        self._current_round_active_players = [p for p in self.players if not p.is_folded and p.chips > 0] # Update after blinds might make someone all-in/fold implicitly
        if self._check_hand_over_due_to_folds(): return 
        self._deal_hole_cards()
        if len([p for p in self._current_round_active_players if not p.is_all_in and not p.is_folded]) > 1 :
            self._conduct_betting_round("Pre-flop")
        self._current_round_active_players = [p for p in self.players if not p.is_folded] 
        if self._check_hand_over_due_to_folds(): return
        if len(self._current_round_active_players) > 1: 
            self._deal_flop()
            if len(self.community_cards) < 3: self._showdown(); return 
            if len([p for p in self._current_round_active_players if not p.is_all_in and not p.is_folded and p.chips > 0]) > 1:
                 self._conduct_betting_round("Flop")
        self._current_round_active_players = [p for p in self.players if not p.is_folded]
        if self._check_hand_over_due_to_folds(): return
        if len(self._current_round_active_players) > 1: 
            self._deal_turn_or_river("Turn")
            if len(self.community_cards) < 4: self._showdown(); return
            if len([p for p in self._current_round_active_players if not p.is_all_in and not p.is_folded and p.chips > 0]) > 1:
                self._conduct_betting_round("Turn")
        self._current_round_active_players = [p for p in self.players if not p.is_folded]
        if self._check_hand_over_due_to_folds(): return
        if len(self._current_round_active_players) > 1: 
            self._deal_turn_or_river("River")
            if len(self.community_cards) < 5: self._showdown(); return
            if len([p for p in self._current_round_active_players if not p.is_all_in and not p.is_folded and p.chips > 0]) > 1:
                self._conduct_betting_round("River")
        self._current_round_active_players = [p for p in self.players if not p.is_folded]
        self._showdown()

    def _check_hand_over_due_to_folds(self, is_betting_round_fold: bool = False) -> bool:
        num_not_folded = sum(1 for p in self.players if not p.is_folded)
        if is_betting_round_fold: # Called from _conduct_betting_round after a fold
            return num_not_folded <= 1 # Signals to betting round to stop if true

        # Called from play_hand (between stages)
        if num_not_folded == 1:
            # Update _current_round_active_players before accessing it for the winner
            self._current_round_active_players = [p for p in self.players if not p.is_folded]
            if self._current_round_active_players : 
                winner = self._current_round_active_players[0]
                print(f"{winner.name} wins the pot of {self.pot} as all other players folded.")
                winner.chips += self.pot; self.pot = 0
            return True
        if num_not_folded == 0: 
            print("Error: No players left in the hand. Pot remains or should be handled.") 
            return True
        return False

```
