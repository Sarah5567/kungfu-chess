# Kung Fu Chess (Python)

Kung Fu Chess is a real-time chess-inspired game written in Python.  
Unlike classic turn-based chess, the game operates in continuous time, where pieces move independently, use state machines, and interact through an event-driven architecture.

The project emphasizes clean software design, separation of concerns, and testability, similar to a lightweight game engine.

---

## Features

- Real-time (non turn-based) chess gameplay
- Event-driven architecture using an internal Event Bus
- Piece state machines (idle, move, short rest, etc.)
- Physics-based movement and collision handling
- Decoupled graphics and rendering layer
- Asset-driven configuration for pieces and animations
- Extensive unit tests for core systems

---

## Project Structure

```
src/
├── app/                 # Application entry point
│   └── main.py
├── core/                # Core game logic
│   ├── game.py
│   ├── board.py
│   ├── moves.py
│   ├── state.py
│   ├── score.py
│   └── table.py
├── pieces/              # Chess piece logic and factories
│   ├── piece.py
│   └── piece_factory.py
├── physics/             # Physics engine
│   ├── physics.py
│   └── physics_factory.py
├── graphics/            # Rendering abstraction
│   ├── graphics.py
│   ├── graphics_factory.py
│   ├── screen.py
│   └── img.py
├── input/               # Input handling and events
│   ├── command.py
│   └── event_bus.py
├── enums/               # Enum-like constants
│   ├── events_names.py
│   └── states_names.py
├── infrastructure/      # Logging utilities
│   └── log.py
└── tests/               # Unit tests
```

---

## Assets

```
assets/
├── pieces/              # Piece animations and state configs
│   └── <piece>/<state>/
│       ├── config.json
│       └── sprites/
├── sounds/              # Sound effects
│   ├── move.wav
│   ├── capture.wav
│   └── victory.wav
```

Each piece state is defined using external JSON configuration and sprite sequences, allowing behavior changes without code modification.

---

## Entry Point

The game starts from:

```bash
python src/app/main.py
```

This file initializes:
- Game loop
- Board
- Physics engine
- Graphics system
- Event bus
- Input commands

---

## Core Concepts

### Event-Driven Design
All major systems communicate via an Event Bus, reducing coupling and improving scalability.

### State Machines
Each piece operates using a state machine (idle, move, rest), enabling real-time behavior and cooldowns.

### Physics Layer
Movement and collisions are handled by a dedicated physics module, independent of rendering and game logic.

### Graphics Abstraction
Rendering is separated from logic, allowing mocking and isolated testing.

---

## Testing

Unit tests are provided for all major subsystems:

- Game logic
- Piece behavior
- Physics engine
- State transitions
- Scoring
- Graphics abstraction
- Logging

Run tests using:

```bash
pytest src/tests
```

---

## Requirements

- Python 3.x
- Additional dependencies may be required depending on the graphics backend

It is recommended to use a virtual environment.

---

## Design Goals

- Clean architecture
- High testability
- Extensibility
- Clear separation of responsibilities
- Game-engine style modularity
