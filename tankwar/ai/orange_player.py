import random
import time
import json
from dataclasses import dataclass

import requests


@dataclass
class ScanResult:
    turn: int
    x: int
    y: int
    color: str
    orientation: int
    turret_orientation: int
    target_x: int
    target_y: int


class OrangePlayer:
    def __init__(self):
        self.color = "orange"
        self.last_turn = None
        self.turn_of_last_scan = None
        # Track estimated position and target between scans
        self.current_x = None
        self.current_y = None
        self.current_orientation = None
        self.target_x = None
        self.target_y = None

    def get_turn(self):
        response = requests.get("http://127.0.0.1:5000/turn")
        return int(response.content.decode("utf-8"))

    def parse_scan_result(self, scan_result_str):
        """
        Parse the scan result JSON string into a ScanResult dataclass.

        Args:
            scan_result_str: JSON string with scan data

        Returns:
            ScanResult object with parsed data
        """
        scan_data = json.loads(scan_result_str)
        scan_data = json.loads(scan_data["scan"])
        try:
            scan_result = ScanResult(
            turn=scan_data["turn"],
            x=scan_data["x"],
            y=scan_data["y"],
            color=scan_data["color"],
            orientation=scan_data["orientation"],
            turret_orientation=scan_data["turret_orientation"],
            target_x=scan_data["target_x"],
            target_y=scan_data["target_y"]
        )
        except:
            scan_result = None
        return scan_result

    def choose_action(self, x, y, orientation, target_x, target_y):
        """
        Choose an action to move toward the target by:
        1. Using current orientation if it's beneficial
        2. Moving along one axis at a time
        3. Turning only when necessary
        """
        print(f"Position: ({x},{y}), Target: ({target_x},{target_y}), Orientation: {orientation}")

        # Check if already at target position
        if x == target_x and y == target_y:
            return "SCAN"



        # First, leverage current orientation
        if orientation == 1:  # NORTH
            if y > target_y:  # Target is above us (north)
                return "FORWARD"
            elif y < target_y:  # Target is below us (south)
                return "BACKWARD"
            else:  # Same y, need to move on x-axis
                return "TURN_RIGHT" if x < target_x else "TURN_LEFT"

        elif orientation == 3:  # SOUTH
            if y < target_y:  # Target is below us (south)
                return "FORWARD"
            elif y > target_y:  # Target is above us (north)
                return "BACKWARD"
            else:  # Same y, need to move on x-axis
                return "TURN_RIGHT" if x > target_x else "TURN_LEFT"

        elif orientation == 4:  # EAST
            if x < target_x:  # Target is to our right (east)
                return "FORWARD"
            elif x > target_x:  # Target is to our left (west)
                return "BACKWARD"
            else:  # Same x, need to move on y-axis
                return "TURN_RIGHT" if y > target_y else "TURN_LEFT"

        elif orientation == 2:  # WEST
            if x > target_x:  # Target is to our left (west)
                return "FORWARD"
            elif x < target_x:  # Target is to our right (east)
                return "BACKWARD"
            else:  # Same x, need to move on y-axis
                return "TURN_RIGHT" if y < target_y else "TURN_LEFT"

        # Fallback action if something unexpected happens
        return "SCAN"

    def play(self):
        current_turn = self.get_turn()
        if current_turn == self.last_turn:
            time.sleep(0.1)
            return
        self.last_turn = current_turn

        # Need to scan if this is the first turn or if it's time for a periodic scan
        need_scan = (self.turn_of_last_scan is None or
                     current_turn - self.turn_of_last_scan >= 5 or
                     self.estimated_x is None)

        if current_turn - self.turn_of_last_scan == 1:
            # If we just scanned, update our estimated position
            self.update_position_from_scan()
        if need_scan:
            action = "SCAN"
            self.turn_of_last_scan = current_turn
        else:
            # Use our estimated position to choose action
            action = self.choose_action(
                self.current_x,
                self.current_y,
                self.current_orientation,
                self.target_x,
                self.target_y
            )

        print(f"AI {self.color} is playing turn {current_turn} with action {action}")
        self.set_action(action, current_turn)

        # Update our estimated position based on action
        if action != "SCAN":
            self.update_position_based_on_action(action)

    def update_position_from_scan(self):
        scan_str = requests.get(f"http://127.0.0.1:5000/scan/{self.color}").content.decode("utf-8")
        scan_result = self.parse_scan_result(scan_str)
        self.current_x = scan_result.x
        self.current_y = scan_result.y
        self.current_orientation = scan_result.orientation
        self.target_x = scan_result.target_x
        self.target_y = scan_result.target_y

    def set_action(self, action_str, turn):
        requests.post(f"http://127.0.0.1:5000/action",json={"action": action_str, "turn": turn, "color": self.color})

