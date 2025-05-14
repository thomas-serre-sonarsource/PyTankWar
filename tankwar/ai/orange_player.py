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
            scan_result = "missing"
        return scan_result

    def play(self):
        current_turn = self.get_turn()
        if current_turn == self.last_turn:
            time.sleep(0.1)
            return
        self.last_turn = current_turn

        if current_turn > 2:
            scan_result_str = requests.get(f"http://127.0.0.1:5000/scan/{self.color}").content.decode("utf-8")
            scan_result = self.parse_scan_result(scan_result_str)

        random_action = random.choice([
                "FORWARD",
                "BACKWARD",
                "TURN_LEFT",
                "TURN_RIGHT",
                "TURN_TURRET_LEFT",
                "TURN_TURRET_RIGHT",
                "FIRE",
                "SCAN"
            ])

        print(f"AI {self.color} is playing turn {current_turn} with action {random_action}")
        self.set_action("SCAN", current_turn)

    def set_action(self, action_str, turn):
        requests.post(f"http://127.0.0.1:5000/action",json={"action": action_str, "turn": turn, "color": self.color})
