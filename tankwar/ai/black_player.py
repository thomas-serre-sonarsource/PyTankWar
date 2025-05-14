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


@dataclass
class ScanResult:
    """Data class to hold scan results for a tank."""

    turn: int
    x: int
    y: int
    color: str
    orientation: int
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

        self.current_orientation = None
        self.last_scan_results = None
        self.path = None

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

        if self.last_action is None or current_turn % 5 == 0:
            logging.info("Performing initial scan")
            next_action = "SCAN"
        elif self.last_action == "SCAN":
            logging.info(
                "Previous action was SCAN - getting results and computing path"
            )
            results = self.get_scan_results()
            self.last_scan_results = results
            logging.info(
                f"Scan results: x={results.x}, y={results.y}, target_x={results.target_x}, target_y={results.target_y}"
            )

            logging.info("Computing path to target")
            self.path = compute_fastest_path(
                results.x, results.y, results.target_x, results.target_y
            )
            logging.info(f"Computed path: {self.path}")

            next_action = orientation_to_action(
                Orientation(self.path[0]),
                Orientation(self.last_scan_results.orientation),
            )
            logging.info(f"Next action based on path: {next_action}")
            self.path.pop(0)
            logging.info(f"Remaining path: {self.path}")
        else:
            logging.info(f"Previous action was {self.last_action} - continuing path")
            next_action = orientation_to_action(
                Orientation(self.path[0]),
                Orientation(self.last_scan_results.orientation),
            )
            logging.info(f"Next action based on path: {next_action}")
            self.path.pop(0)
            logging.info(f"Remaining path: {self.path}")

        if self.current_orientation is not None:
            old_orientation = self.current_orientation
            self.current_orientation = update_orientation(
                self.current_orientation, next_action
            )
            logging.info(
                f"Updated orientation: {old_orientation} -> {self.current_orientation}"
            )

        logging.info(f"Setting action: {next_action} for turn {current_turn}")
        self.set_action(next_action, current_turn)
        self.last_action = next_action

    def set_action(self, action_str, turn):
        if action_str not in POSSIBLE_ACTIONS:
            raise ValueError(f"Invalid action: {action_str}")
        requests.post(
            "http://127.0.0.1:5000/action",
            json={"action": action_str, "turn": turn, "color": self.color},
        )

    def get_scan_results(self):
        """Fetch and print the scan results for the black tank."""
        response = requests.get(f"http://127.0.0.1:5000/scan/{self.color}")
        scan_data = response.json()
        if scan_data:
            logging.info(f"Scan results for {self.color} tank: {scan_data['scan']}")
        else:
            logging.info(f"No scan results available for {self.color} tank")
        return ScanResult.from_dict(json.loads(scan_data["scan"]))


def get_wrapped_distance(x1: int, y1: int, x2: int, y2: int) -> Tuple[int, int]:
    """
    Calculate the shortest distance between two points on a wrapping grid.
    Returns the x and y differences that represent the shortest path.
    """
    # Calculate direct distance
    dx = x2 - x1
    dy = y2 - y1

    # # Calculate wrapped distance
    # wrapped_dx = (
    #     dx - GRID_SIZE
    #     if dx > GRID_SIZE // 2
    #     else dx + GRID_SIZE
    #     if dx < -GRID_SIZE // 2
    #     else dx
    # )
    # wrapped_dy = (
    #     dy - GRID_SIZE
    #     if dy > GRID_SIZE // 2
    #     else dy + GRID_SIZE
    #     if dy < -GRID_SIZE // 2
    #     else dy
    # )

    wrapped_dx = dx
    wrapped_dy = dy

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


def compute_fastest_path(x: int, y: int, x_target: int, y_target: int) -> List[int]:
    """
    Compute the fastest path from (x,y) to (x_target, y_target) on a wrapping grid.
    Returns a list of orientations (1-4) representing the sequence of moves needed.

    Orientations:
    1: Right
    2: Down
    3: Left
    4: Up
    """
    path = []
    current_x, current_y = x, y

    while current_x != x_target or current_y != y_target:
        # Calculate the shortest distance considering wrapping
        dx, dy = get_wrapped_distance(current_x, current_y, x_target, y_target)

        # Choose the direction with the largest difference
        if abs(dx) > abs(dy):
            # Move horizontally
            orientation = 1 if dx > 0 else 3
            current_x = (current_x + (1 if dx > 0 else -1)) % GRID_SIZE
        else:
            # Move vertically
            orientation = 2 if dy > 0 else 4
            current_y = (current_y + (1 if dy > 0 else -1)) % GRID_SIZE

        path.append(orientation)

    return [Orientation(orientation) for orientation in path]


def orientation_to_action(
    target_orientation: Orientation, current_orientation: Orientation
) -> str:
    if target_orientation == current_orientation:
        return "FORWARD"
    elif current_orientation == Orientation.NORTH:
        if target_orientation == Orientation.EAST:
            return "TURN_RIGHT"
        elif target_orientation == Orientation.WEST:
            return "TURN_LEFT"
        elif target_orientation == Orientation.SOUTH:
            return "TURN_LEFT"
    elif current_orientation == Orientation.EAST:
        if target_orientation == Orientation.SOUTH:
            return "TURN_RIGHT"
        elif target_orientation == Orientation.NORTH:
            return "TURN_LEFT"
        elif target_orientation == Orientation.WEST:
            return "TURN_LEFT"
    elif current_orientation == Orientation.SOUTH:
        if target_orientation == Orientation.WEST:
            return "TURN_RIGHT"
        elif target_orientation == Orientation.EAST:
            return "TURN_LEFT"
        elif target_orientation == Orientation.NORTH:
            return "TURN_LEFT"
    elif current_orientation == Orientation.WEST:
        if target_orientation == Orientation.NORTH:
            return "TURN_RIGHT"
        elif target_orientation == Orientation.SOUTH:
            return "TURN_LEFT"
        elif target_orientation == Orientation.EAST:
            return "TURN_LEFT"
    else:
        raise ValueError(
            f"Invalid orientation: {target_orientation} {current_orientation}"
        )


def update_orientation(orientation: Orientation, action: str) -> Orientation:
    if action == "FORWARD":
        return orientation
    elif action == "BACKWARD":
        return orientation - 2
    else:
        return orientation + 1


def int_to_orientation(orientation: int) -> Orientation:
    if orientation == 1:
        return Orientation.NORTH
    elif orientation == 2:
        return Orientation.EAST
    elif orientation == 3:
        return Orientation.SOUTH
    elif orientation == 4:
        return Orientation.WEST
    else:
        raise ValueError(f"Invalid orientation: {orientation}")
