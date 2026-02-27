# ZorkGPT: AI Beats Zork — 350/350, Master Adventurer

**Claude (Opus) completed Zork I with a perfect score using only CLI tools, reasoning, and a persistent knowledge base. No hardcoded solutions.**

```
Your score is 350 (total of 350 points), in 630 moves.
This gives you the rank of Master Adventurer.
```

> See the full victory narrative in [`report.md`](report.md) and the complete turn-by-turn log in `game_files/.session/narrative.log`.

## What Happened

Claude Code, running as an interactive agent through a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code/skills), played Zork I to completion. It solved every puzzle, collected all 19 treasures, and reached the Stone Barrow endgame in 604 turns — earning the maximum 350 points and the rank of Master Adventurer.

The agent:
- Navigated 85+ rooms across the Great Underground Empire
- Solved complex multi-step puzzles (coal-to-diamond machine, Hades bell/book/candles ritual, thief egg-opening sequence, Frigid River boat expedition)
- Managed inventory across narrow passages and basket transport mechanisms
- Built and maintained a knowledge base and location-specific memories
- Used 113 save checkpoints for safe experimentation
- Recovered from failures by restoring checkpoints and trying new strategies

## Two Ways to Play

This repository supports two modes of AI gameplay:

### 1. Claude Code Interactive Mode (used for the victory)

Claude plays Zork directly through CLI tools in a conversational session. This is how the 350-point victory was achieved.

```bash
# Prerequisites: Python 3.11+, uv, Claude Code CLI

# Setup
git clone https://github.com/Zedmor/ZorkGPT
cd ZorkGPT
uv sync

# Tell Claude to play
# In Claude Code, just say: "play Zork"
# Or invoke the skill: /play-zork
```

Claude uses `zork_cli.py` to interact with the Z-machine game engine, reading and writing to markdown files for persistent memory. The skill file at `.claude/skills/play-zork/SKILL.md` teaches Claude the gameplay loop, memory protocols, and puzzle-solving strategies.

**How it works:**

1. Claude reads `game_files/knowledgebase.md` (strategic wisdom) and `game_files/Memories.md` (location memories)
2. Each turn: Claude calls `zork_cli.py send-command "<action>"` and receives JSON with game response, location, score, inventory, and movement data
3. Claude reasons about what to do next based on game text + Z-machine structured data
4. After discoveries, Claude writes memories and knowledge base updates directly to markdown files
5. Before risky actions, Claude saves checkpoints; on failure, it restores and tries a different approach

**CLI tool reference:**

| Command | Purpose |
|---------|---------|
| `start-game` | Initialize a new game session |
| `send-command "<cmd>"` | Send a game command, get JSON response |
| `get-state` | Get full state (location, inventory, objects, exits) |
| `validate-action "<cmd>"` | Check action against Z-machine object tree |
| `save-checkpoint "<name>"` | Save named checkpoint |
| `restore-checkpoint "<name>"` | Restore a checkpoint |
| `get-map` | Get explored map as Mermaid diagram |
| `look` | Shortcut for `send-command "look"` |

### 2. Autonomous Orchestrator Mode (original system)

The original ZorkGPT system runs multi-turn episodes autonomously using multiple specialized LLMs (Agent, Critic, Extractor, Strategy Generator) coordinated by an orchestrator.

```bash
# Configure API keys
cp .env.example .env
# Edit .env with your LLM API keys

# Run an autonomous episode
uv run python main.py
```

See [Architecture](#architecture) below for full details on the orchestrator system.

## Key Insight: Why Claude Code Works

The Claude Code approach succeeds because it collapses the multi-LLM orchestrator into a single reasoning agent with direct tool access:

| Orchestrator Mode | Claude Code Mode |
|---|---|
| Agent LM generates action | Claude reasons about action |
| Critic LM evaluates action | Claude uses `validate-action` |
| Extractor LM parses game text | `send-command` returns structured JSON |
| Strategy Generator synthesizes knowledge | Claude writes to `knowledgebase.md` directly |
| Memory Manager synthesizes memories | Claude writes to `Memories.md` directly |
| Map Manager tracks movement | `zork_cli.py` auto-updates map on movement |
| Orchestrator coordinates all managers | Claude does everything in one conversation |

The Z-machine still does the heavy lifting — providing ground-truth location IDs, inventory, score, object trees, and valid exits. Claude just gets to use all of that data directly instead of through multiple intermediary LLM calls.

## Architecture

### Claude Code Skill Architecture

```
Claude Code Session
    |
    |-- Reads: game_files/knowledgebase.md    (strategic wisdom)
    |-- Reads: game_files/Memories.md         (location memories)
    |
    |-- Calls: zork_cli.py send-command       (each turn)
    |     |
    |     |-- JerichoInterface                (Z-machine access)
    |     |     |-- get_location_structured() (room ID + name)
    |     |     |-- get_inventory_structured() (item list)
    |     |     |-- get_score()               (current score)
    |     |     |-- get_visible_objects()      (object tree)
    |     |     `-- get_valid_exits()          (ground-truth exits)
    |     |
    |     |-- MovementAnalyzer                (ID-based movement detection)
    |     |-- MapGraph                        (auto-updated map)
    |     `-- Returns: JSON response
    |
    |-- Calls: zork_cli.py save-checkpoint    (before risky actions)
    |-- Calls: zork_cli.py restore-checkpoint (on failure)
    |-- Calls: zork_cli.py validate-action    (before uncertain actions)
    |-- Calls: zork_cli.py get-state          (for full state inspection)
    |-- Calls: zork_cli.py get-map            (for navigation planning)
    |
    |-- Writes: game_files/Memories.md        (after discoveries)
    `-- Writes: game_files/knowledgebase.md   (after puzzle solutions)
```

### Original Orchestrator Architecture

The full autonomous system uses a modular architecture coordinated by `ZorkOrchestratorV2`:

- **Agent LM** — Action generation with knowledge integration
- **Critic LM** — Two-stage evaluation: fast object tree validation + LLM assessment
- **Extractor LM** — Hybrid Z-machine + LLM parsing
- **Strategy Generator LM** — Turn-window analysis and knowledge synthesis
- **Managers** — Objective, Knowledge, Map, Memory, State, Context, Episode, Rejection

All components share access to the Jericho Z-machine interface for ground-truth game state.

## Project Structure

```
ZorkGPT/
├── README.md                           # This file
├── report.md                           # Victory report (350/350)
├── zork_cli.py                         # CLI tool for Claude Code gameplay
├── .claude/skills/play-zork/SKILL.md   # Claude Code skill definition
├── game_files/
│   ├── knowledgebase.md                # Strategic wisdom (cross-episode)
│   ├── Memories.md                     # Location-specific memories
│   └── .session/                       # Game state persistence
│       ├── game_state.pkl              # Z-machine state
│       ├── session.json                # Turn/score tracking
│       ├── map_state.json              # Explored map graph
│       ├── narrative.log               # Human-readable game log
│       └── checkpoints/                # Named save points (113 total)
│           └── victory-350pts/         # The winning checkpoint
├── game_interface/core/
│   └── jericho_interface.py            # Z-machine access layer
├── orchestration/
│   └── zork_orchestrator_v2.py         # Autonomous orchestrator
├── managers/                           # Specialized manager modules
├── map_graph.py                        # Graph-based map + Mermaid rendering
├── movement_analyzer.py                # ID-based movement detection
├── zork_agent.py                       # Agent LM
├── zork_critic.py                      # Critic LM
├── hybrid_zork_extractor.py            # Extractor LM
└── tests/                              # Test suite
```

## Running Tests

```bash
# Fast test suite (skip slow tests)
uv run pytest tests/ -k "not slow" -q

# Run specific test file
uv run pytest tests/test_map_persistence.py -v

# Full suite with detailed output
uv run pytest tests/ -xvs --tb=short
```

## Core Design Principles

1. **All game reasoning from LLMs** — No hardcoded puzzle solutions or predetermined game mechanics
2. **Z-machine first** — Use structured data from the game engine (location IDs, object trees, score) instead of parsing text
3. **Integer-based room IDs** — Stable identity from Z-machine memory, no room name fragmentation
4. **Source-location memory storage** — Memories stored where they were learned, enabling cross-episode learning
5. **Checkpoint-based experimentation** — Save before risk, restore on failure, try again with new knowledge

## Credits

- **Original ZorkGPT** by [stickystyle](https://github.com/stickystyle/ZorkGPT) — the orchestrator architecture, Jericho integration, and manager system
- **Zork I** by Infocom (1980) — the game itself, running via the [Jericho](https://github.com/microsoft/jericho) Z-machine library
- **Claude Code skill and CLI** — the interactive gameplay interface added in this fork
- **Victory achieved by** Claude (Opus) playing through Claude Code
