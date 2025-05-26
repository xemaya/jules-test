from core.game import Game
from ai.player import AIPlayer, Player # Import Player as well for potential human players later
from core.card import Card # For potentially showing player hands more explicitly if needed

def print_player_chips(players: list[Player]):
    print("\n--- Player Chip Counts ---")
    for player in players:
        print(f"{player.name}: {player.chips} chips")
    print("--------------------------\n")

def main():
    # Setup Players
    player1 = AIPlayer(name="Alice (AI)", chips=1000)
    player2 = AIPlayer(name="Bob (AI)", chips=1000)
    player3 = AIPlayer(name="Charlie (AI)", chips=1000)
    # player4 = Player(name="Human Dave", chips=1000) # Example for a human player

    players = [player1, player2, player3] # Add player4 here for human testing

    # Initialize Game
    game = Game(players=players, initial_dealer_pos=0) # Start dealer at player 0

    num_hands_to_play = 10  # Or some other condition
    for hand_num in range(1, num_hands_to_play + 1):
        print(f"==================== HAND #{hand_num} ====================")
        
        # Check for bankrupt players before starting a hand
        active_players_for_hand = [p for p in game.players if p.chips > 0]
        if len(active_players_for_hand) < 2:
            print("Not enough players with chips to continue. Game over.")
            break
        
        # Update the game's player list if players went bankrupt and were removed
        # (Game class currently doesn't remove players, it just marks them as folded or they can't bet if 0 chips)
        # For simplicity, we'll let the game logic handle players with 0 chips (they should be skipped or auto-fold)
        # A more robust solution might involve removing players from the game.players list or having a status.
        
        game.play_hand() # This method should handle one full hand of poker
        
        print_player_chips(game.players) # Show chip counts after the hand

        # Check for game end condition (e.g., only one player has all the chips)
        players_with_chips = [p for p in game.players if p.chips > 0]
        if len(players_with_chips) == 1:
            print(f"Game over! {players_with_chips[0].name} has won all the chips!")
            break
        if hand_num == num_hands_to_play and num_hands_to_play > 0 : # Check if max hands reached (and not infinite play)
            print(f"Played {num_hands_to_play} hands. Game session ended.")
            break # Ensure loop terminates if num_hands_to_play is the limit

    print("\n--- Final Chip Counts ---")
    for player in game.players:
        print(f"{player.name}: {player.chips} chips")
    print("==========================")

if __name__ == "__main__":
    main()
```
