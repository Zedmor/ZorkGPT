#!/usr/bin/env python3
"""CLI tool for playing Zork via Jericho. Outputs JSON to stdout.

Each invocation creates a JerichoInterface, loads persisted state from disk,
executes the requested command, saves state back, and prints JSON to stdout.

Usage:
    uv run python zork_cli.py start-game
    uv run python zork_cli.py send-command "open mailbox"
    uv run python zork_cli.py get-state
    uv run python zork_cli.py validate-action "take sword"
    uv run python zork_cli.py save-checkpoint "before-troll"
    uv run python zork_cli.py restore-checkpoint "before-troll"
    uv run python zork_cli.py get-map
    uv run python zork_cli.py look
"""

import argparse
import json
import pickle
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from game_interface.core.jericho_interface import JerichoInterface
from map_graph import MapGraph, DIRECTION_MAPPING, normalize_direction
from movement_analyzer import MovementAnalyzer

# Map truncated Z-machine dictionary words to canonical direction names
_EXIT_NORMALIZATION = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up", "d": "down",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "north": "north", "south": "south", "east": "east", "west": "west",
    "up": "up", "down": "down",
    "northeast": "northeast", "northwest": "northwest",
    "southeast": "southeast", "southwest": "southwest",
    "northe": "northeast", "northw": "northwest",
    "southe": "southeast", "southw": "southwest",
    "in": "in", "inside": "in", "into": "in",
    "out": "out",
}

_PROJECT_ROOT = Path(__file__).resolve().parent
SESSION_DIR = _PROJECT_ROOT / "game_files" / ".session"
STATE_FILE = SESSION_DIR / "game_state.pkl"
SESSION_FILE = SESSION_DIR / "session.json"
MAP_FILE = SESSION_DIR / "map_state.json"
CHECKPOINT_DIR = SESSION_DIR / "checkpoints"
GAME_FILE = str(_PROJECT_ROOT / "jericho-game-suite" / "zork1.z5")
NARRATIVE_LOG = SESSION_DIR / "narrative.log"


def _log_narrative(text: str):
    """Append a line to the narrative game log."""
    try:
        _ensure_session_dir()
        with open(NARRATIVE_LOG, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass  # Never let logging break gameplay


def _output(data: dict):
    """Print JSON to stdout and exit cleanly."""
    json.dump(data, sys.stdout, indent=2)
    print()  # trailing newline


def _error(message: str, code: int = 1):
    """Print error JSON to stdout and exit."""
    _output({"error": message})
    sys.exit(code)


def _ensure_session_dir():
    """Create session directory structure."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


def _load_session():
    """Load Jericho state + session metadata + map from disk.

    Returns:
        Tuple of (JerichoInterface, session_dict, MapGraph)
    """
    if not STATE_FILE.exists():
        _error("No active game session. Run 'start-game' first.")

    # Create interface and start engine (needed to restore state)
    game_path = GAME_FILE
    jericho = JerichoInterface(game_path)
    try:
        jericho.start()

        # SECURITY: pickle.load is used intentionally here. State files are
        # written by this process and stored in a user-controlled local directory.
        with open(STATE_FILE, "rb") as f:
            state = pickle.load(f)
        jericho.restore_state(state)

        # Load session metadata
        with open(SESSION_FILE, "r") as f:
            session = json.load(f)

        # Load map
        game_map = MapGraph()
        if MAP_FILE.exists():
            with open(MAP_FILE, "r") as f:
                map_data = json.load(f)
            game_map = MapGraph.from_dict(map_data)

        return jericho, session, game_map
    except SystemExit:
        raise
    except Exception:
        jericho.close()
        raise


def _save_session(jericho: JerichoInterface, session: dict, game_map: MapGraph):
    """Save Jericho state + session metadata + map to disk."""
    _ensure_session_dir()

    # Save Z-machine state
    state = jericho.save_state()
    with open(STATE_FILE, "wb") as f:
        pickle.dump(state, f)

    # Save session metadata
    with open(SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)

    # Save map
    with open(MAP_FILE, "w") as f:
        json.dump(game_map.to_dict(), f, indent=2)


def _get_location_info(jericho: JerichoInterface) -> dict:
    """Extract current location info from Z-machine."""
    location = jericho.get_location_structured()
    return {
        "location_id": location.num if location else None,
        "location_name": location.name if location else "Unknown",
    }


def _get_inventory_list(jericho: JerichoInterface) -> list:
    """Get inventory as a list of item names."""
    return [obj.name for obj in jericho.get_inventory_structured()]


def _get_score_info(jericho: JerichoInterface) -> dict:
    """Get score information."""
    score, max_score = jericho.get_score()
    return {"score": score, "max_score": max_score}


def _normalize_exits(raw_exits: list) -> list:
    """Normalize Z-machine dictionary exit words to canonical direction names."""
    canonical = set()
    for exit_word in raw_exits:
        normalized = _EXIT_NORMALIZATION.get(exit_word.lower().strip())
        if normalized:
            canonical.add(normalized)
    return sorted(canonical)


def _get_visible_objects_info(jericho: JerichoInterface) -> list:
    """Get visible objects with their attributes."""
    visible = jericho.get_visible_objects_in_location()
    result = []
    for obj in visible:
        attrs = jericho.get_object_attributes(obj)
        # Only include attributes that are True
        active_attrs = {k: v for k, v in attrs.items() if v}
        result.append({
            "name": obj.name,
            "id": obj.num,
            "attributes": active_attrs,
        })
    return result


# --- Subcommand handlers ---


def cmd_start_game(args):
    """Start a new game session."""
    _ensure_session_dir()

    # Check for existing session
    if STATE_FILE.exists() and not args.force:
        _error(
            "Game session already exists. Use 'start-game --force' to start fresh, "
            "or use 'send-command' to continue playing."
        )

    game_path = GAME_FILE
    if not Path(GAME_FILE).exists():
        _error(f"Game file not found: {GAME_FILE}")

    # Initialize game
    jericho = JerichoInterface(game_path)
    try:
        intro_text = jericho.start()

        # Send 'verbose' for full room descriptions
        jericho.send_command("verbose")

        # Get initial state
        loc = _get_location_info(jericho)
        score_info = _get_score_info(jericho)

        # Create map with initial room
        game_map = MapGraph()
        game_map.add_room(loc["location_id"], loc["location_name"])

        # Create session metadata
        session = {
            "episode_id": str(uuid.uuid4())[:8],
            "turn": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "score_history": [{"turn": 0, "score": score_info["score"]}],
        }

        # Save everything
        _save_session(jericho, session, game_map)
    finally:
        jericho.close()

    # Write narrative log header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Truncate old log on new game
    try:
        _ensure_session_dir()
        with open(NARRATIVE_LOG, "w", encoding="utf-8") as f:
            f.write(f"{'=' * 60}\n")
            f.write(f"  ZORK I — Episode {session['episode_id']}\n")
            f.write(f"  Started: {timestamp}\n")
            f.write(f"{'=' * 60}\n\n")
            f.write(intro_text + "\n\n")
    except Exception:
        pass

    _output({
        "intro_text": intro_text,
        **loc,
        **score_info,
        "inventory": [],
        "episode_id": session["episode_id"],
    })


def cmd_send_command(args):
    """Send a command to the game."""
    command = args.cmd
    if not command or not command.strip():
        _error("Empty command")

    jericho, session, game_map = _load_session()
    analyzer = MovementAnalyzer()

    try:
        # Capture state before command
        before_loc = _get_location_info(jericho)
        before_score = _get_score_info(jericho)

        # Execute command
        response = jericho.send_command(command)

        # Capture state after command
        after_loc = _get_location_info(jericho)
        after_score = _get_score_info(jericho)

        # Detect movement
        movement = analyzer.analyze_movement(
            before_loc["location_id"],
            after_loc["location_id"],
            command,
        )
        moved = movement.movement_occurred

        # Auto-update map on movement
        if moved:
            # Ensure both rooms exist in map
            game_map.add_room(before_loc["location_id"], before_loc["location_name"])
            game_map.add_room(after_loc["location_id"], after_loc["location_name"])

            # Determine direction for connection
            normalized = normalize_direction(command.strip())
            if normalized:
                game_map.add_connection(
                    before_loc["location_id"],
                    normalized,
                    after_loc["location_id"],
                )

        # Check for game over
        game_over, game_over_reason = jericho.is_game_over(response)

        # Get inventory before saving (need live jericho)
        inventory = _get_inventory_list(jericho) if not game_over else []

        # Update session
        session["turn"] += 1
        score_changed = after_score["score"] != before_score["score"]
        if score_changed:
            session["score_history"].append({
                "turn": session["turn"],
                "score": after_score["score"],
            })

        # Save
        _save_session(jericho, session, game_map)
    finally:
        jericho.close()

    result = {
        "response": response,
        **after_loc,
        **after_score,
        "inventory": inventory,
        "turn": session["turn"],
        "moved": moved,
        "game_over": game_over,
        "game_over_reason": game_over_reason,
    }
    if score_changed:
        result["score_change"] = after_score["score"] - before_score["score"]
    if moved:
        result["from_location"] = before_loc["location_name"]
        result["from_location_id"] = before_loc["location_id"]

    # Narrative log
    turn = session["turn"]
    score = after_score["score"]
    lines = [f"[Turn {turn}] ({after_loc['location_name']}, Score: {score})"]
    lines.append(f"> {command}")
    lines.append(response)
    if score_changed:
        delta = after_score["score"] - before_score["score"]
        lines.append(f"  *** Score: {before_score['score']} -> {score} ({'+' if delta > 0 else ''}{delta}) ***")
    if moved:
        lines.append(f"  [Moved: {before_loc['location_name']} -> {after_loc['location_name']}]")
    if game_over:
        lines.append(f"\n{'=' * 40}")
        lines.append(f"  GAME OVER: {game_over_reason}")
        lines.append(f"  Final Score: {score}/{after_score['max_score']} in {turn} turns")
        lines.append(f"{'=' * 40}")
    lines.append("")
    _log_narrative("\n".join(lines))

    _output(result)


def cmd_get_state(args):
    """Get current game state without executing a command."""
    jericho, session, game_map = _load_session()

    try:
        loc = _get_location_info(jericho)
        score_info = _get_score_info(jericho)
        inventory = _get_inventory_list(jericho)
        visible = _get_visible_objects_info(jericho)
        valid_exits = _normalize_exits(jericho.get_valid_exits())
    finally:
        jericho.close()

    _output({
        **loc,
        **score_info,
        "inventory": inventory,
        "visible_objects": visible,
        "valid_exits": valid_exits,
        "turn": session["turn"],
        "episode_id": session["episode_id"],
    })


def cmd_validate_action(args):
    """Validate an action against the Z-machine object tree."""
    action = args.action
    if not action or not action.strip():
        _error("Empty action")

    jericho, session, game_map = _load_session()

    try:
        result = _validate_against_object_tree(action, jericho)
    finally:
        jericho.close()

    _output(result)


def _validate_against_object_tree(action: str, jericho: JerichoInterface) -> dict:
    """Validate action against Z-machine object tree.

    Ported from zork_critic.py:599-731 with simplification.
    """
    try:
        parts = action.lower().strip().split(maxsplit=1)
        if len(parts) < 2:
            return {"valid": True, "reason": "Single word command", "confidence": 1.0}

        verb = parts[0]
        target = parts[1]

        # Strip prepositional phrases
        prepositions = ['from', 'in', 'with', 'to', 'at', 'on', 'under', 'behind', 'into']
        for prep in prepositions:
            prep_pattern = f' {prep} '
            if prep_pattern in target:
                target = target.split(prep_pattern)[0]
                break

        # Validate "take" actions
        if verb in ['take', 'get', 'grab', 'pick']:
            targets = [t.strip() for t in target.split(',')]
            visible_objects = jericho.get_visible_objects_in_location()
            inventory_objects = jericho.get_inventory_structured()

            # Build accessible objects list (including contents of transparent containers)
            all_accessible = list(visible_objects) + list(inventory_objects)
            world_objects = jericho.env.get_world_objects()

            def add_accessible_children(obj_list):
                new_objects = []
                for obj in obj_list:
                    attrs = jericho.get_object_attributes(obj)
                    if attrs.get('transparent'):
                        for child_obj in world_objects:
                            if child_obj.parent == obj.num and child_obj not in all_accessible:
                                new_objects.append(child_obj)
                                all_accessible.append(child_obj)
                return new_objects

            current_level = list(visible_objects) + list(inventory_objects)
            while current_level:
                current_level = add_accessible_children(current_level)

            for single_target in targets:
                found = any(single_target in obj.name.lower() for obj in all_accessible)
                if not found:
                    return {
                        "valid": False,
                        "reason": f"Object '{single_target}' is not visible or accessible",
                        "confidence": 0.9,
                    }

        # Validate "open/close" actions
        elif verb in ['open', 'close']:
            visible_objects = jericho.get_visible_objects_in_location()
            found = False
            for obj in visible_objects:
                if target in obj.name.lower():
                    attrs = jericho.get_object_attributes(obj)
                    if attrs.get('openable') or attrs.get('container'):
                        found = True
                        break
                    else:
                        return {
                            "valid": False,
                            "reason": f"Object '{target}' cannot be opened/closed",
                            "confidence": 0.9,
                        }

            if not found:
                return {
                    "valid": False,
                    "reason": f"Object '{target}' is not present",
                    "confidence": 0.9,
                }

        return {"valid": True, "reason": "Action allowed", "confidence": 1.0}

    except Exception as e:
        return {"valid": True, "reason": f"Validation error ({e}) - defaulting to allow", "confidence": 0.5}


def cmd_save_checkpoint(args):
    """Save a named checkpoint."""
    name = args.name
    if not name or not name.strip():
        _error("Empty checkpoint name")

    # Validate name (alphanumeric, hyphens, underscores only)
    safe_name = name.strip()
    if not all(c.isalnum() or c in '-_' for c in safe_name):
        _error("Checkpoint name must be alphanumeric (hyphens and underscores allowed)")

    if not STATE_FILE.exists():
        _error("No active game session. Run 'start-game' first.")

    _ensure_session_dir()
    checkpoint_path = CHECKPOINT_DIR / safe_name

    try:
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(STATE_FILE, checkpoint_path / "game_state.pkl")
        shutil.copy2(SESSION_FILE, checkpoint_path / "session.json")
        if MAP_FILE.exists():
            shutil.copy2(MAP_FILE, checkpoint_path / "map_state.json")

        _log_narrative(f"  [Checkpoint saved: \"{safe_name}\"]\n")

        _output({
            "success": True,
            "checkpoint_name": safe_name,
            "message": f"Checkpoint '{safe_name}' saved",
        })

    except Exception as e:
        _error(f"Failed to save checkpoint: {e}")


def cmd_restore_checkpoint(args):
    """Restore a named checkpoint."""
    name = args.name
    if not name or not name.strip():
        _error("Empty checkpoint name")

    safe_name = name.strip()
    checkpoint_path = CHECKPOINT_DIR / safe_name

    if not checkpoint_path.exists():
        # List available checkpoints
        available = [d.name for d in CHECKPOINT_DIR.iterdir() if d.is_dir()] if CHECKPOINT_DIR.exists() else []
        _error(f"Checkpoint '{safe_name}' not found. Available: {available}")

    try:
        shutil.copy2(checkpoint_path / "game_state.pkl", STATE_FILE)
        shutil.copy2(checkpoint_path / "session.json", SESSION_FILE)
        map_checkpoint = checkpoint_path / "map_state.json"
        if map_checkpoint.exists():
            shutil.copy2(map_checkpoint, MAP_FILE)

        # Return current state after restore
        jericho, session, game_map = _load_session()
        try:
            loc = _get_location_info(jericho)
            score_info = _get_score_info(jericho)
            inventory = _get_inventory_list(jericho)
        finally:
            jericho.close()

        _log_narrative(
            f"  [Checkpoint restored: \"{safe_name}\" — "
            f"back to Turn {session['turn']}, {loc['location_name']}, "
            f"Score: {score_info['score']}]\n"
        )

        _output({
            "restored": True,
            "checkpoint_name": safe_name,
            **loc,
            **score_info,
            "inventory": inventory,
            "turn": session["turn"],
        })

    except Exception as e:
        _error(f"Failed to restore checkpoint: {e}")


def cmd_get_map(args):
    """Get the current game map."""
    if not MAP_FILE.exists():
        _error("No map data. Start a game first.")

    try:
        with open(MAP_FILE, "r") as f:
            map_data = json.load(f)
        game_map = MapGraph.from_dict(map_data)

        # Get current location from session
        current_location_id = None
        if SESSION_FILE.exists():
            jericho, session, _ = _load_session()
            try:
                loc = _get_location_info(jericho)
                current_location_id = loc["location_id"]
            finally:
                jericho.close()

        rooms = {str(rid): room.name for rid, room in game_map.rooms.items()}
        total_connections = sum(len(c) for c in game_map.connections.values())

        _output({
            "mermaid_diagram": game_map.render_mermaid(),
            "rooms": rooms,
            "current_location_id": current_location_id,
            "total_rooms": len(game_map.rooms),
            "total_connections": total_connections,
        })

    except Exception as e:
        _error(f"Failed to get map: {e}")


def cmd_look(args):
    """Convenience: equivalent to send-command 'look'."""
    from types import SimpleNamespace
    cmd_send_command(SimpleNamespace(cmd="look"))


def main():
    parser = argparse.ArgumentParser(
        description="ZorkGPT CLI — play Zork via Jericho, outputs JSON to stdout"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # start-game
    p_start = subparsers.add_parser("start-game", help="Start a new game session")
    p_start.add_argument("--force", action="store_true", help="Overwrite existing session")

    # send-command
    p_send = subparsers.add_parser("send-command", help="Send a command to the game")
    p_send.add_argument("cmd", help="Game command to send (e.g., 'open mailbox')")

    # get-state
    subparsers.add_parser("get-state", help="Get current game state without executing a command")

    # validate-action
    p_validate = subparsers.add_parser("validate-action", help="Validate an action against the object tree")
    p_validate.add_argument("action", help="Action to validate (e.g., 'take sword')")

    # save-checkpoint
    p_save = subparsers.add_parser("save-checkpoint", help="Save a named checkpoint")
    p_save.add_argument("name", help="Checkpoint name (alphanumeric, hyphens, underscores)")

    # restore-checkpoint
    p_restore = subparsers.add_parser("restore-checkpoint", help="Restore a named checkpoint")
    p_restore.add_argument("name", help="Checkpoint name to restore")

    # get-map
    subparsers.add_parser("get-map", help="Get the current game map as Mermaid diagram")

    # look
    subparsers.add_parser("look", help="Equivalent to send-command 'look'")

    args = parser.parse_args()

    # Dispatch
    handlers = {
        "start-game": cmd_start_game,
        "send-command": cmd_send_command,
        "get-state": cmd_get_state,
        "validate-action": cmd_validate_action,
        "save-checkpoint": cmd_save_checkpoint,
        "restore-checkpoint": cmd_restore_checkpoint,
        "get-map": cmd_get_map,
        "look": cmd_look,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        _error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _error(f"Unexpected error: {e}")
