# Dungeon Duel: Rogue AI

A 2D turn-based dungeon crawler game built with Python and Pygame. The player competes against an intelligent AI monster in a procedurally generated dungeon. The AI uses advanced algorithms for pathfinding, decision-making, and combat.

## Features

- Grid-based dungeon map with random generation
- Player and AI take alternate turns
- AI uses:
  - A\* Search for pathfinding
  - Simulated Annealing for movement decision
  - Naive Bayes Classifier to predict player behavior
  - Min-Max for combat decisions
- Treasures, potions, and obstacles randomly placed
- Modular codebase for easy extension
- Visual UI using Pygame

## Directory Structure

```
dungeon_duel/
│
├── main.py                # Game launcher
├── config.py              # Constants (grid size, tile types, etc.)
├── dungeon.py             # Map generation logic
├── player.py              # Player movement and actions
├── ai_monster.py          # AI logic (A*, Annealing, Min-Max, Naive Bayes)
├── engine.py              # Turn handling, state control
├── ui.py                  # Pygame display code
├── combat.py              # Combat mechanics
├── assets/                # Sprites, sounds, fonts
├── models/                # Naive Bayes model training and prediction
├── utils/                 # Logging, random placement tools
└── README.md              # Game instructions
```

## Requirements

- Python 3.8+
- pygame
- numpy
- scikit-learn

## Setup

1. Install dependencies:
   ```bash
   pip install pygame numpy scikit-learn
   ```
2. Run the game:
   ```bash
   python main.py
   ```

## How to Play

- Use arrow keys to move your character.
- Collect treasures and potions, avoid obstacles.
- Defeat the AI monster to win!

## License

MIT
