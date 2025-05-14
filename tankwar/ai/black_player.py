import time
import requests
import logging
import traceback
import sys
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from ..logic.orientation import Orientation

LOG_FILE = "black_player.log"
GRID_SIZE = 50

# Clear the log file before starting
with open(LOG_FILE, "w") as f:
    f.write("")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def exc_handler(exctype, value, tb):
    logging.exception("".join(traceback.format_exception(exctype, value, tb)))


sys.excepthook = exc_handler

POSSIBLE_ACTIONS = [
    "FORWARD",
    "BACKWARD",
    "TURN_LEFT",
    "TURN_RIGHT",
    "TURN_TURRET_LEFT",
    "TURN_TURRET_RIGHT",
    "FIRE",
    "SCAN",
]

# Orientation transition maps
_TURN_RIGHT_MAP = {
    Orientation.NORTH: Orientation.EAST,
    Orientation.EAST: Orientation.SOUTH,
    Orientation.SOUTH: Orientation.WEST,
    Orientation.WEST: Orientation.NORTH,
}

_TURN_LEFT_MAP = {
    Orientation.NORTH: Orientation.WEST,
    Orientation.WEST: Orientation.SOUTH,
    Orientation.SOUTH: Orientation.EAST,
    Orientation.EAST: Orientation.NORTH,
}


@dataclass
class ScanResult:
    """Data class to hold scan results for a tank."""

    turn: int
    x: int
    y: int
    color: str
    orientation: int  # This is an integer from the server
    turret_orientation: int
    target_x: Optional[int] = None
    target_y: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScanResult":
        """Create a ScanResult instance from a dictionary."""
        return cls(**data)


class BlackPlayer:
    def __init__(self):
        self.color = "black"
        self.last_turn = None
        self.last_action = None

        self.current_orientation: Optional[Orientation] = (
            None  # Stores Orientation enum
        )
        self.last_scan_results: Optional[ScanResult] = None
        self.path: Optional[List[Orientation]] = None

    def get_turn(self):
        response = requests.get("http://127.0.0.1:5000/turn")
        return int(response.content.decode("utf-8"))

    def play(self):
        current_turn = self.get_turn()
        logging.info(f"Current turn: {current_turn}, Last turn: {self.last_turn}")

        if current_turn == self.last_turn:
            time.sleep(0.1)
            return

        self.last_turn = current_turn
        logging.info(f"Processing new turn {current_turn}")

        next_action = None

        if self.last_action is None or current_turn % 10 == 0:
            logging.info("Performing initial scan or periodic scan")
            next_action = "SCAN"
        elif self.last_action == "SCAN":
            logging.info(
                "Previous action was SCAN - getting results and computing path"
            )
            results = self.get_scan_results()
            if results:
                self.last_scan_results = results
                # Update current orientation from scan results
                self.current_orientation = int_to_orientation(results.orientation)
                logging.info(
                    f"Scan results: x={results.x}, y={results.y}, target_x={results.target_x}, target_y={results.target_y}, orientation={self.current_orientation}"
                )

                if results.target_x is not None and results.target_y is not None:
                    logging.info("Computing path to target")
                    self.path = compute_fastest_path(
                        results.x,
                        results.y,
                        results.target_x,
                        results.target_y,
                        self.current_orientation,
                    )
                    logging.info(f"Computed path: {self.path}")

                    if self.path:
                        target_path_orientation = self.path[0]
                        next_action = orientation_to_action(
                            target_path_orientation, self.current_orientation
                        )
                        logging.info(f"Next action based on path: {next_action}")
                        if next_action == "FORWARD":  # Only pop if moving forward
                            self.path.pop(0)
                        logging.info(f"Remaining path: {self.path}")
                    else:
                        logging.warning("Path computation resulted in an empty path.")
                        next_action = "SCAN"  # Fallback if path is empty
                else:
                    logging.warning("Target not found in scan results, rescanning.")
                    next_action = "SCAN"
            else:
                logging.error("Failed to get scan results, will try SCAN again.")
                next_action = "SCAN"  # Fallback if scan fails

        elif self.path and self.current_orientation is not None:  # Continuing path
            logging.info(f"Previous action was {self.last_action} - continuing path")
            if not self.path:  # Path might have been exhausted
                logging.info("Path exhausted, performing scan.")
                next_action = "SCAN"
            else:
                target_path_orientation = self.path[0]
                next_action = orientation_to_action(
                    target_path_orientation, self.current_orientation
                )
                logging.info(f"Next action based on path: {next_action}")
                if next_action == "FORWARD":  # Only pop if moving forward
                    self.path.pop(0)
                logging.info(f"Remaining path: {self.path}")
        else:
            logging.warning(
                f"No path or current_orientation, forcing SCAN. Path: {self.path}, Orientation: {self.current_orientation}"
            )
            next_action = "SCAN"  # Fallback

        if next_action:
            if (
                self.current_orientation is not None
            ):  # Can only update if orientation is known
                old_orientation = self.current_orientation
                # Update internal model of orientation based on the decided action
                self.current_orientation = update_orientation(
                    self.current_orientation, next_action
                )
                logging.info(
                    f"Updated internal orientation: {old_orientation} -> {self.current_orientation} after deciding action {next_action}"
                )
            else:
                logging.info(
                    f"Current orientation is None, cannot update. Action: {next_action}"
                )

            logging.info(f"Setting action: {next_action} for turn {current_turn}")
            self.set_action(next_action, current_turn)
            self.last_action = next_action
        else:
            # This case should ideally not be reached if logic is sound, implies an issue.
            logging.error("No action determined, this is a bug. Defaulting to SCAN.")
            self.set_action("SCAN", current_turn)
            self.last_action = "SCAN"

    def set_action(self, action_str, turn):
        if action_str not in POSSIBLE_ACTIONS:
            # Log error but allow game to proceed with a default action perhaps?
            # For now, raise error as it's a critical issue for AI dev.
            logging.error(f"Invalid action attempted: {action_str}")
            raise ValueError(f"Invalid action: {action_str}")
        requests.post(
            "http://127.0.0.1:5000/action",
            json={"action": action_str, "turn": turn, "color": self.color},
        )

    def get_scan_results(self) -> Optional[ScanResult]:
        """Fetch and print the scan results for the black tank."""
        try:
            response = requests.get(f"http://127.0.0.1:5000/scan/{self.color}")
            response.raise_for_status()  # Raise an exception for HTTP errors
            scan_data = response.json()
            if scan_data and "scan" in scan_data and scan_data["scan"]:
                # The server sends scan data as a JSON string within a JSON object
                actual_scan_dict = json.loads(scan_data["scan"])
                logging.info(f"Scan results for {self.color} tank: {actual_scan_dict}")
                return ScanResult.from_dict(actual_scan_dict)
            else:
                logging.warning(
                    f"No scan results or empty scan data available for {self.color} tank. Response: {scan_data}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching scan results: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.error(
                f"Error decoding scan results JSON: {e}. Response text: {response.text if 'response' in locals() else 'N/A'}"
            )
            return None


def get_wrapped_distance(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    """
    Calculate the shortest distance between two points on a wrapping grid.
    Returns the x and y differences that represent the shortest path.
    """
    # Calculate direct distance
    dx = x2 - x1
    dy = y2 - y1

    # Calculate wrapped distance
    wrapped_dx = (
        dx - GRID_SIZE
        if dx > GRID_SIZE // 2
        else dx + GRID_SIZE
        if dx < -GRID_SIZE // 2
        else dx
    )
    wrapped_dy = (
        dy - GRID_SIZE
        if dy > GRID_SIZE // 2
        else dy + GRID_SIZE
        if dy < -GRID_SIZE // 2
        else dy
    )
    # The original code had this, which disables wrapping.
    # wrapped_dx = dx
    # wrapped_dy = dy

    return wrapped_dx, wrapped_dy


def get_orientation_for_direction(dx: int, dy: int) -> int:
    # The gris starts from the top left being (0, 0)

    if dx == 0 and dy == 1:
        return 2
    elif dx == 1 and dy == 0:
        return 1
    elif dx == 0 and dy == -1:
        return 4
    elif dx == -1 and dy == 0:
        return 3
    else:
        raise ValueError(f"Invalid direction: dx={dx}, dy={dy}")


def get_opposite_orientation(orientation: Orientation) -> Orientation:
    if orientation == Orientation.NORTH:
        return Orientation.SOUTH
    if orientation == Orientation.EAST:
        return Orientation.WEST
    if orientation == Orientation.SOUTH:
        return Orientation.NORTH
    if orientation == Orientation.WEST:
        return Orientation.EAST
    # Should not happen with valid Orientation enum
    raise ValueError(f"Invalid orientation for get_opposite: {orientation}")


def compute_fastest_path(
    x: int,
    y: int,
    x_target: int,
    y_target: int,
    current_tank_orientation: Optional[Orientation] = None,
) -> List[Orientation]:
    """
    Compute the fastest path from (x,y) to (x_target, y_target) on a wrapping grid.
    Returns a list of Orientations representing the sequence of MOVEMENT FACINGS needed.
    Prefers continuing in a straight line if possible.
    The first step considers current_tank_orientation to avoid immediate 180-degree turns if a 90-degree alternative exists.
    """
    path_orientations: List[Orientation] = []
    current_x, current_y = x, y

    max_path_len = 2 * GRID_SIZE

    for step_num in range(max_path_len):
        if current_x == x_target and current_y == y_target:
            break

        dx, dy = get_wrapped_distance(current_x, current_y, x_target, y_target)
        chosen_orientation: Optional[Orientation] = None
        log_action_type = "greedy"  # Default log type

        if dx == 0 and dy == 0:  # Should be caught by loop condition check too
            logging.debug(
                f"compute_fastest_path: Target reached at ({current_x},{current_y}). Step: {step_num}"
            )
            break

        if step_num == 0:  # Logic for the very first segment of the path
            # 1. Determine pure greedy first step
            pure_greedy_first_step: Optional[Orientation] = None
            if abs(dx) > abs(dy):
                pure_greedy_first_step = (
                    Orientation.EAST if dx > 0 else Orientation.WEST
                )
            elif abs(dy) > abs(dx):
                pure_greedy_first_step = (
                    Orientation.SOUTH if dy > 0 else Orientation.NORTH
                )
            else:  # abs(dx) == abs(dy), and not both zero
                if dx > 0:
                    pure_greedy_first_step = Orientation.EAST
                elif dx < 0:
                    pure_greedy_first_step = Orientation.WEST
                elif dy > 0:
                    pure_greedy_first_step = Orientation.SOUTH
                elif dy < 0:
                    pure_greedy_first_step = Orientation.NORTH

            chosen_orientation = pure_greedy_first_step
            log_action_type = "first_greedy"

            if pure_greedy_first_step and current_tank_orientation:
                if pure_greedy_first_step == get_opposite_orientation(
                    current_tank_orientation
                ):
                    logging.debug(
                        f"Path Step 0: Greedy choice ({pure_greedy_first_step}) is 180 deg from current ({current_tank_orientation}). Exploring 90 deg alternatives."
                    )
                    # Greedy choice is a 180 turn. Explore 90-degree alternatives.
                    alt_orientation: Optional[Orientation] = None
                    can_move_east = dx > 0
                    can_move_west = dx < 0
                    can_move_south = dy > 0
                    can_move_north = dy < 0

                    # Determine potential 90-degree turn directions
                    left_turn_orientation = _TURN_LEFT_MAP[current_tank_orientation]
                    right_turn_orientation = _TURN_RIGHT_MAP[current_tank_orientation]

                    # Check if left turn is valid and makes progress
                    if left_turn_orientation == Orientation.EAST and can_move_east:
                        alt_orientation = Orientation.EAST
                    elif left_turn_orientation == Orientation.WEST and can_move_west:
                        alt_orientation = Orientation.WEST
                    elif left_turn_orientation == Orientation.SOUTH and can_move_south:
                        alt_orientation = Orientation.SOUTH
                    elif left_turn_orientation == Orientation.NORTH and can_move_north:
                        alt_orientation = Orientation.NORTH

                    # If left turn wasn't chosen, check right turn (or if both are valid, this could be refined)
                    if not alt_orientation:
                        if right_turn_orientation == Orientation.EAST and can_move_east:
                            alt_orientation = Orientation.EAST
                        elif (
                            right_turn_orientation == Orientation.WEST and can_move_west
                        ):
                            alt_orientation = Orientation.WEST
                        elif (
                            right_turn_orientation == Orientation.SOUTH
                            and can_move_south
                        ):
                            alt_orientation = Orientation.SOUTH
                        elif (
                            right_turn_orientation == Orientation.NORTH
                            and can_move_north
                        ):
                            alt_orientation = Orientation.NORTH

                    if alt_orientation:
                        logging.debug(
                            f"Path Step 0: Avoiding 180 turn. Chosen alternative: {alt_orientation}"
                        )
                        chosen_orientation = alt_orientation
                        log_action_type = "first_alt_90deg"
                    else:
                        logging.debug(
                            f"Path Step 0: No suitable 90deg turn found. Sticking with 180deg greedy: {pure_greedy_first_step}"
                        )
        else:  # Logic for subsequent segments (step_num > 0)
            last_planned_move = path_orientations[-1]
            # Try to continue straight
            if last_planned_move == Orientation.EAST and dx > 0:
                chosen_orientation = Orientation.EAST
            elif last_planned_move == Orientation.WEST and dx < 0:
                chosen_orientation = Orientation.WEST
            elif last_planned_move == Orientation.SOUTH and dy > 0:
                chosen_orientation = Orientation.SOUTH
            elif last_planned_move == Orientation.NORTH and dy < 0:
                chosen_orientation = Orientation.NORTH

            if chosen_orientation:
                log_action_type = "straight"
            else:
                # Fallback to greedy if cannot continue straight
                log_action_type = "greedy_fallback"
                if abs(dx) > abs(dy):
                    chosen_orientation = (
                        Orientation.EAST if dx > 0 else Orientation.WEST
                    )
                elif abs(dy) > abs(dx):
                    chosen_orientation = (
                        Orientation.SOUTH if dy > 0 else Orientation.NORTH
                    )
                else:  # abs(dx) == abs(dy), and not both zero
                    if dx > 0:
                        chosen_orientation = Orientation.EAST
                    elif dx < 0:
                        chosen_orientation = Orientation.WEST
                    elif dy > 0:
                        chosen_orientation = Orientation.SOUTH
                    elif dy < 0:
                        chosen_orientation = Orientation.NORTH

        # Update position based on the decided orientation
        if chosen_orientation == Orientation.EAST:
            current_x = (current_x + 1) % GRID_SIZE
        elif chosen_orientation == Orientation.WEST:
            current_x = (current_x - 1 + GRID_SIZE) % GRID_SIZE
        elif chosen_orientation == Orientation.SOUTH:
            current_y = (current_y + 1) % GRID_SIZE
        elif chosen_orientation == Orientation.NORTH:
            current_y = (current_y - 1 + GRID_SIZE) % GRID_SIZE

        if chosen_orientation:
            logging.debug(
                f"Path step {step_num}: To ({current_x},{current_y}). Target: ({x_target},{y_target}). Move: {chosen_orientation}, Type: {log_action_type}, dx:{dx}, dy:{dy}"
            )
            path_orientations.append(chosen_orientation)
        else:
            logging.error(
                f"compute_fastest_path: No orientation chosen at step {step_num}. "
                f"current=({x},{y}), internal_curr=({current_x},{current_y}), target=({x_target},{y_target}), dx={dx}, dy={dy}. Breaking."
            )
            break

    if not path_orientations and (x != x_target or y != y_target):
        logging.warning(
            f"Path computation resulted in empty path but not at target. Start:({x},{y}), Target:({x_target},{y_target})"
        )
    elif len(path_orientations) >= max_path_len:
        logging.warning(
            f"Path computation reached max length ({max_path_len}). current=({current_x},{current_y}), target=({x_target},{y_target})"
        )

    return path_orientations


def orientation_to_action(
    target_orientation: Orientation, current_orientation: Orientation
) -> str:
    if target_orientation == current_orientation:
        return "FORWARD"

    # Check if one turn right aligns
    if _TURN_RIGHT_MAP[current_orientation] == target_orientation:
        return "TURN_RIGHT"

    # Check if one turn left aligns (or two right turns)
    if _TURN_LEFT_MAP[current_orientation] == target_orientation:
        return "TURN_LEFT"

    # If target is 180 degrees away, it will take two turns.
    # Prefer TURN_RIGHT as the first of two turns.
    # Example: Current=N, Target=S. _TURN_RIGHT_MAP[N] = E. E is not S. _TURN_LEFT_MAP[N] = W. W is not S.
    # So it defaults to TURN_RIGHT. Tank becomes E. Next turn: Current=E, Target=S -> TURN_RIGHT. Correct.
    return "TURN_RIGHT"


def update_orientation(orientation: Orientation, action: str) -> Orientation:
    if action == "TURN_LEFT":
        return _TURN_LEFT_MAP[orientation]
    elif action == "TURN_RIGHT":
        return _TURN_RIGHT_MAP[orientation]
    # Actions that do not change chassis orientation
    elif action in [
        "FORWARD",
        "BACKWARD",
        "FIRE",
        "SCAN",
        "TURN_TURRET_LEFT",
        "TURN_TURRET_RIGHT",
    ]:
        return orientation
    else:
        # Should not happen with POSSIBLE_ACTIONS
        logging.warning(
            f"Unknown action '{action}' in update_orientation, orientation not changed."
        )
        return orientation


def int_to_orientation(orientation_val: int) -> Orientation:
    # Server orientation: 1=N, 2=E, 3=S, 4=W (Assumed based on original int_to_orientation)
    # Our Enum: NORTH = 1, WEST = 2, SOUTH = 3, EAST = 4
    if orientation_val == 1:  # North
        return Orientation.NORTH
    elif orientation_val == 2:  # East
        return Orientation.EAST
    elif orientation_val == 3:  # South
        return Orientation.SOUTH
    elif orientation_val == 4:  # West
        return Orientation.WEST
    else:
        logging.error(
            f"Invalid integer orientation value from server: {orientation_val}"
        )
        # Fallback to a default or raise error. For now, NORTH.
        # Consider if this state is recoverable or implies a major sync issue.
        return Orientation.NORTH
