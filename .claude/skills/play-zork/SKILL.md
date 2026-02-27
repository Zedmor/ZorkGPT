---
name: play-zork
description: >
  Play the classic text adventure Zork I using CLI tools.
  Use when the user says "play Zork", "start Zork", or wants to play
  a text adventure game. Claude becomes the game-playing agent —
  reasoning out loud, making decisions, managing memory and knowledge.
allowed-tools:
  - Bash(uv run python zork_cli.py *)
  - Read
  - Edit
  - Write
  - Glob
  - Grep
---

# Skill: Play Zork

Play the classic text adventure Zork I using CLI tools. You ARE the game-playing agent — reason out loud, make decisions, manage memory and knowledge.

## Episode Start Sequence

**Every episode MUST begin with these steps in order:**

1. **Read knowledge** — strategic context for the whole game:
   ```
   Read game_files/knowledgebase.md
   ```
2. **Read memories** — location-specific tactical context:
   ```
   Read game_files/Memories.md
   ```
3. **Start or restore game:**
   ```bash
   uv run python zork_cli.py start-game        # new game
   uv run python zork_cli.py restore-checkpoint "name"  # resume
   ```
4. **Get initial state** to know where you are:
   ```bash
   uv run python zork_cli.py get-state
   ```
5. **Look up current location** in memories (see Location Memory Lookup below).

## Gameplay Loop (Every Turn)

```
1. Receive send-command response (location, score, inventory, movement)
2. IF location changed:
   a. Location Memory Lookup — grep Memories.md for this location ID
   b. If memories exist → read them, factor into next decision
   c. If knowledgebase has relevant entries (danger, puzzle) → review them
3. Reason out loud about what to do next
4. IF a memory/knowledge write trigger fires → write immediately (see triggers below)
5. Choose and execute next action
```

### Location Memory Lookup

When `send-command` returns a new location, **immediately** check for existing memories:

```
Grep pattern="ID: <location_id>" path="game_files/Memories.md" output_mode="content" -A=5
```

- **Memories found**: Read them. Apply known solutions. Avoid known failures. Skip re-exploring what's already documented.
- **No memories**: This is a new location. Explore thoroughly (look, examine objects, check exits). Write a memory after discovering anything notable.

Also check the knowledgebase for relevant context:

```
Grep pattern="ID: <location_id>" path="game_files/knowledgebase.md" output_mode="content" -A=3
```

Before attempting any puzzle, check:
```
Grep pattern="<puzzle keyword>" path="game_files/knowledgebase.md" output_mode="content" -A=5
```

## CLI Tool Reference

All commands output JSON to stdout. Run via `uv run python zork_cli.py <subcommand>`.

### `start-game [--force]`
Initialize a new game session. Use `--force` to overwrite an existing session. Returns intro text, starting location, and score.

### `send-command "<command>"`
Send a game command. Returns the game's text response plus structured data: location, score, inventory, movement detection, and game-over status. The map is auto-updated when movement is detected.

### `get-state`
Get full game state without executing a command. Returns location, score, inventory, visible objects with attributes, and valid exits (ground-truth from Z-machine). Use this when you need to assess your situation.

### `validate-action "<action>"`
Check if an action is valid against the Z-machine object tree before executing. Does NOT change game state. Use for "take/get/open/close" commands when uncertain if the target object exists. Returns `{valid, reason, confidence}`.

### `save-checkpoint "<name>"`
Save a named checkpoint (full game state + map + session). Use before risky actions (combat, irreversible choices). Names must be alphanumeric with hyphens/underscores.

### `restore-checkpoint "<name>"`
Restore a previously saved checkpoint. Fully reverts game state, map, and session metadata.

### `get-map`
Get the explored map as a Mermaid diagram plus room list and statistics. Useful for navigation planning. The diagram uses `L<id>` node IDs matching Z-machine location IDs.

### `look`
Convenience shortcut for `send-command "look"`.

## Game Mechanics — Parser Reference

**Format:** VERB-NOUN (1-3 words max). The parser recognizes only the first 6 letters of each word.

**Core Commands:**
- **Movement:** n/s/e/w, north/south/east/west, up/down, in/out, enter/exit
- **Observation:** look, examine [object], read [object]
- **Manipulation:** take/drop [object], open/close [object], push/pull [object]
- **Combat:** attack [enemy] with [weapon]
- **Utility:** inventory (i), wait
- **Multi-object:** `take lamp, jar, sword` or `take all` or `drop all except key`
- **NPC interaction:** `[name], [command]` (e.g., `gnome, give me the key`)

**One command per turn.** You may chain non-movement actions with commas (`take sword, light lamp`), but NEVER chain movement commands.

## Puzzle-Solving Protocol

1. **Check knowledgebase first**: Before attempting any puzzle, grep `game_files/knowledgebase.md` for the location or puzzle keywords. If a solution exists, follow it.
2. **Distinguish failure types:**
   - **Hard failure** ("There is a wall there", "I don't understand"): Stop after 2 attempts
   - **Puzzle feedback** (dynamic responses, state changes): Continue experimenting with DIFFERENT approaches
3. **Systematic experimentation:** Standard verbs -> Synonyms -> Environmental verbs -> Item combinations -> State changes
4. **Environmental clues:** Read room descriptions carefully. Emphasized adjectives/sensory details are puzzle hints.

## Memory Protocol

Read and write `game_files/Memories.md` directly using Read/Edit tools.

### Memory Format

```markdown
## Location: Room Name (ID: <location_id>)

**[SUCCESS - PERMANENT] Action description** *(Ep<N>, T<turn>, +<score_change>)*
What happened and what was learned.

**[FAILURE - PERMANENT] Action description** *(Ep<N>, T<turn>, +0)*
What went wrong and why.
```

### Memory Rules

- Store memories at the SOURCE location (where you were when you learned it)
- Use location IDs from CLI output (e.g., `ID: 180` for West of House)
- Mark score-gaining actions as SUCCESS, failed attempts as FAILURE
- Check existing memories before writing to avoid duplicates
- Append new memories to the end of an existing location section, or create a new section if the location doesn't exist yet

### Memory Write Triggers (Write Immediately When These Occur)

**Note:** Some triggers (puzzle solved, death) require writing to BOTH Memories.md AND knowledgebase.md. Do both.

| Trigger | What to Write |
|---|---|
| **Puzzle solved** | SUCCESS entry with exact command sequence and score change (also update knowledgebase) |
| **Death or major failure** | FAILURE entry with what went wrong and how to avoid it (also update knowledgebase) |
| **Score increase** | SUCCESS entry noting the action that caused the score change |
| **New area with notable content** | Entry describing key objects, exits, and any items found |
| **Failed approach after 3+ attempts** | FAILURE entry to prevent repeating in future episodes |

## Knowledge Protocol

Read `game_files/knowledgebase.md` at episode start. Update it during gameplay when triggers fire.

### Knowledge Sections

| Section | Content |
|---|---|
| **DANGERS & THREATS** | Enemies, environmental hazards, traps, and how to avoid/defeat them |
| **PUZZLE SOLUTIONS** | Puzzle mechanics, required items, exact command sequences |
| **STRATEGIC PATTERNS** | Inventory management, route planning, general tactics |
| **COMMAND SYNTAX** | Parser quirks, exact phrasing that works vs. doesn't |
| **CROSS-EPISODE INSIGHTS** | Validated patterns, environmental facts, meta-strategies, major discoveries |

### Knowledge Write Triggers

| Trigger | Section to Update |
|---|---|
| **Puzzle solved** | PUZZLE SOLUTIONS — add location, items needed, exact commands |
| **Death** | DANGERS & THREATS — add cause, recognition pattern, prevention |
| **New parser quirk discovered** | COMMAND SYNTAX — add working vs. failing phrasing |
| **Every ~20 turns or session end** | STRATEGIC PATTERNS — review recent actions, note effective/ineffective approaches |
| **Knowledgebase entry proven wrong** | Edit or remove the incorrect entry immediately |

### Cross-Episode Learning Workflow

**Before acting, consult knowledge:**
- Entering a potentially dangerous area? → Check DANGERS & THREATS
- Encountering a puzzle? → Check PUZZLE SOLUTIONS
- Unsure of exact command phrasing? → Check COMMAND SYNTAX
- Planning a route? → Check STRATEGIC PATTERNS and CROSS-EPISODE INSIGHTS

**After significant events, update knowledge:**
- Solved a new puzzle not in knowledgebase → add to PUZZLE SOLUTIONS
- Died in a new way → add to DANGERS & THREATS
- Discovered a faster route or better strategy → update STRATEGIC PATTERNS
- Confirmed a pattern across multiple plays → promote to CROSS-EPISODE INSIGHTS

## Strategy

1. **Explore systematically:** New room → look → examine objects → try exits → map
2. **Combat priority:** When enemies appear (sword glows), ONLY use combat actions. No inventory management until safe.
3. **Save checkpoints:** Before combat, before irreversible actions, before entering dangerous areas
4. **Use the map:** Run `get-map` when feeling lost. Plan routes using the Mermaid diagram.
5. **Validate before acting:** Use `validate-action` for take/open commands when unsure
6. **Score tracking:** Note score changes in `send-command` output. Score increases = progress.

## Subagent Protocols

### Memory Synthesis (every ~20 turns or on revisiting a known location)
Spawn a subagent to review recent game actions and write memories to `game_files/Memories.md`. The subagent should read the file first to avoid duplicates.

### Strategic Analysis (at episode end or score plateau)
Spawn a subagent to analyze the game session and update `game_files/knowledgebase.md` with new insights about dangers, puzzles, and strategies.

### Map Analysis (when feeling lost)
Run `get-map` and analyze the Mermaid diagram to identify unexplored areas and plan routes to them.

## Anti-Patterns to Avoid

- Repeating the exact same command after a hard rejection
- Checking inventory during combat
- Chaining multiple movement commands
- Ignoring the map when stuck (use `get-map`)
- Moving away from puzzles that give NEW feedback each turn
- Skipping `validate-action` before risky take/open commands
- Ignoring existing memories when visiting a known location
- Attempting a puzzle without checking knowledgebase first
- Forgetting to write a memory after a significant discovery or failure
