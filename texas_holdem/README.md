# Texas Hold'em Poker Game

A text-based implementation of the popular Texas Hold'em poker game, supporting multiple AI players. This project is built using Python.

## Features

*   **Core Texas Hold'em Logic**: Implements standard rules for hand progression (Pre-flop, Flop, Turn, River).
*   **Hand Evaluation**: Robustly evaluates 5-card poker hands from Royal Flush down to High Card, including correct kicker handling and Ace-low/high straights.
*   **Player Representation**: Supports multiple players, with a basic AI (`AIPlayer`) capable of making random decisions (fold, check, call, raise).
*   **Betting Mechanics**: Includes logic for posting blinds, managing bets, raises, calls, folds, and all-in scenarios. Pot calculation and awarding are handled.
*   **Text-Based Interface**: Playable via the command line, showing game progress, player actions, community cards, and hand results.
*   **Unit Tests**: Basic unit tests for core components (Card, Deck, Hand Evaluation) to ensure reliability.

## Project Structure

```
texas_holdem/
├── main.py             # Main script to run the game
├── core/               # Core game logic
│   ├── __init__.py
│   ├── card.py         # Card class
│   ├── deck.py         # Deck class
│   ├── game.py         # Game class managing game flow, betting rounds, etc.
│   └── hand_evaluator.py # Logic for evaluating poker hands
├── ai/                 # AI and player logic
│   ├── __init__.py
│   └── player.py       # Player and AIPlayer classes
├── utils/              # Utility functions (currently minimal)
│   └── __init__.py
├── tests/              # Unit tests
│   ├── __init__.py
│   ├── test_card_deck.py
│   ├── test_game.py
│   └── test_hand_evaluator.py
└── README.md           # This file
```

## How to Run the Game

1.  Ensure you have Python 3 installed.
2.  Navigate to the `texas_holdem` project directory in your terminal.
    ```bash
    cd path/to/your/texas_holdem
    ```
3.  Run the main script:
    ```bash
    python main.py
    ```
4.  The game will start, and you'll see the actions of AI players printed to the console. The game will play for a predefined number of hands (currently 10) or until one player has all the chips.

## How to Run Tests

1.  Navigate to the `texas_holdem` project root directory.
2.  Run the unit tests using Python's `unittest` module:
    ```bash
    python -m unittest discover tests
    ```
    Alternatively, you can run individual test files:
    ```bash
    python -m unittest tests.test_hand_evaluator
    ```

## Future Improvements (Optional)

*   **Graphical User Interface (GUI)**: Develop a visual interface instead of text-based.
*   **Advanced AI**: Implement more sophisticated AI decision-making logic.
*   **Human Players**: Allow human players to interact with the game via command-line input.
*   **Network Play**: Enable multiple players to play over a network.
*   **Configuration**: Add options for game settings (e.g., starting chips, blind levels, number of players).
```
