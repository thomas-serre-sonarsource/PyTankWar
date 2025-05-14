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

        if self.last_action is None or current_turn % 5 == 0:
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
                        results.x, results.y, results.target_x, results.target_y
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


def compute_fastest_path(
    x: int, y: int, x_target: int, y_target: int
) -> List[Orientation]:
    """
    Compute the fastest path from (x,y) to (x_target, y_target) on a wrapping grid.
    Returns a list of Orientations representing the sequence of MOVEMENT FACINGS needed.
    """
    path: List[Orientation] = []
    current_x, current_y = x, y

    # Limit path length to avoid infinite loops in case of issues
    max_path_len = 2 * GRID_SIZE

    while (current_x != x_target or current_y != y_target) and len(path) < max_path_len:
        dx, dy = get_wrapped_distance(current_x, current_y, x_target, y_target)

        chosen_orientation: Optional[Orientation] = None
        if abs(dx) >= abs(
            dy
        ):  # Prefer horizontal if distances are equal or dx is larger
            if dx > 0:
                chosen_orientation = Orientation.EAST
                current_x = (current_x + 1) % GRID_SIZE
            elif dx < 0:
                chosen_orientation = Orientation.WEST
                current_x = (current_x - 1 + GRID_SIZE) % GRID_SIZE
            # if dx is 0, this block might be skipped if dy is also 0.
            # The while loop condition (current_x != x_target or current_y != y_target) handles this.

        # if chosen_orientation is None and dy != 0: # if no horizontal move was made and vertical move is possible
        # elif abs(dy) > abs(dx): # Original logic: strictly greater
        # Prioritize move if not yet chosen or if vertical is distinctly larger
        if (
            chosen_orientation is None and dy != 0
        ):  # If horizontal was zero, consider vertical
            if dy > 0:
                chosen_orientation = Orientation.SOUTH
                current_y = (current_y + 1) % GRID_SIZE
            elif dy < 0:
                chosen_orientation = Orientation.NORTH
                current_y = (current_y - 1 + GRID_SIZE) % GRID_SIZE
        elif chosen_orientation is None and dx == 0 and dy == 0:
            # This case means we are at the target, loop should terminate.
            # Added for safety, though while condition should catch it.
            break

        if chosen_orientation:
            path.append(chosen_orientation)
        else:
            # This could happen if dx and dy are both zero, meaning we are at the target.
            # The loop condition should handle this. If it's reached, log it.
            logging.warning(
                f"Path computation: dx={dx}, dy={dy} led to no chosen orientation. current=({current_x},{current_y}), target=({x_target},{y_target})"
            )
            break  # Should be at target

    if len(path) >= max_path_len:
        logging.warning(
            f"Path computation exceeded max length. current=({current_x},{current_y}), target=({x_target},{y_target})"
        )

    return path


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
