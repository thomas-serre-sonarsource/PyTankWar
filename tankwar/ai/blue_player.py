import json
import random
import time
import requests
from dataclasses import dataclass
from typing import Optional
from ..logic.orientation import Orientation
import logging


@dataclass
class ScanResult:
    turn: int
    x: int
    y: int
    color: str
    orientation: Orientation
    turret_orientation: Orientation
    target_x: int
    target_y: int

@dataclass
class Point:
    x: int
    y: int

class State:
    ASKED_FOR_SCAN = 0
    SCANNING = 1
    ROTATING = 2
    MOVING = 3
    TARGETING = 4
    WAIT_FOR_TARGET_SHOT = 5
    MID_SCAN = 6
    ASKED_FOR_MID_SCAN = 7


class BluePlayer:
    def __init__(self):
        self.color = "blue"
        self.last_turn = None
        self.state = State.ASKED_FOR_SCAN
        self.scan = ScanResult(0, 0, 0, self.color, Orientation.NORTH, Orientation.NORTH, 0, 0)

    def get_turn(self):
        response = requests.get("http://127.0.0.1:5000/turn")
        return int(response.content.decode("utf-8"))

    def play(self):
        try:
            self.inner_play()
        except Exception as e:
            print(f"Error in BluePlayer: {e}")

    def inner_play(self):
        current_turn = self.get_turn()
        if current_turn == self.last_turn:
            return 

        if current_turn == 0:
            self.state = State.ASKED_FOR_SCAN

        print(f"current turn: {current_turn}, current state: {self.state}")

        if current_turn % 7 == 1 and self.state in (State.MOVING, State.WAIT_FOR_TARGET_SHOT):
            self.old_state = self.state
            self.state = State.ASKED_FOR_MID_SCAN

        if self.state == State.ASKED_FOR_SCAN:
            self.set_action("SCAN", current_turn)
            self.state = State.SCANNING
        elif self.state == State.SCANNING:
            self.scan = self.get_scan()
            print(self.scan)
            self.state = State.MOVING
        elif self.state == State.ROTATING:
            self.do_rotating()
            self.state = State.MOVING
        elif self.state == State.MOVING:
            self.forward()
            print(f"Waiting for {self.scan.x} = {self.scan.target_x} and {self.scan.y} = {self.scan.target_y}")
            if self.scan.target_x == self.scan.x or self.scan.target_y == self.scan.y:
                self.state = State.TARGETING
        elif self.state == State.TARGETING:
            self.fire()
            self.state = State.WAIT_FOR_TARGET_SHOT
        elif self.state == State.WAIT_FOR_TARGET_SHOT:
            self.set_action("SCAN", current_turn)
        elif self.state == State.ASKED_FOR_MID_SCAN:
            self.set_action("SCAN", current_turn)
            self.state = State.MID_SCAN
        elif self.state == State.MID_SCAN:
            self.scan = self.get_scan()
            print(self.scan)
            self.state = State.MOVING
        return




        self.last_turn = current_turn
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
        
        print(f"{self.color} is playing turn {current_turn} with action {random_action}")
        self.set_action(random_action, current_turn)

    def do_rotating(self):
        diff_x = self.scan.target_x - self.scan.x
        diff_y = self.scan.target_y - self.scan.y


    def get_scan(self) -> ScanResult:
        try:
            response = requests.get(f"http://127.0.0.1:5000/scan/{self.color}")
            if response.status_code == 200:
                data = response.json()

                if not data or 'scan' not in data:
                    raise Exception(f"Invalid scan data: {data}")

                scan_data = json.loads(data.get('scan'))
                
                # Convert orientation values to Orientation enum
                orientation_value = scan_data.get('orientation')
                turret_orientation_value = scan_data.get('turret_orientation')
                
                orientation = Orientation(orientation_value) if orientation_value is not None else None
                turret_orientation = Orientation(turret_orientation_value) if turret_orientation_value is not None else None
                
                if orientation is None or turret_orientation is None:
                    raise Exception(f"Invalid orientation values: {orientation_value}, {turret_orientation_value}, json: {scan_data}")

                return ScanResult(
                    turn=scan_data.get('turn'),
                    x=scan_data.get('x'),
                    y=scan_data.get('y'),
                    color=scan_data.get('color'),
                    orientation=orientation,
                    turret_orientation=turret_orientation,
                    target_x=scan_data.get('target_x'),
                    target_y=scan_data.get('target_y')
                )
            else:
                raise Exception(f"Error getting scan: {response.status_code}")
        except Exception as e:
            raise Exception(f"Error getting scan: {e}") from e
    
    def forward(self):
        self.set_action("FORWARD", self.get_turn())
        match self.scan.orientation:
            case Orientation.NORTH:
                self.scan.y -= 1
            case Orientation.SOUTH:
                self.scan.y += 1
            case Orientation.EAST:
                self.scan.x -= 1
            case Orientation.WEST:
                self.scan.x += 1

        self.scan.x = self.scan.x % 50
        self.scan.y = self.scan.y % 50
        print(f"Moving to {self.scan.x}, {self.scan.y}")

    def rotate(self, new_orientation: Orientation):
        if new_orientation == Orientation.NORTH:
            self.set_action("TURN_LEFT", self.get_turn())
            self.scan.orientation = Orientation.WEST
        elif new_orientation == Orientation.SOUTH:
            self.set_action("TURN_RIGHT", self.get_turn())
            self.scan.orientation = Orientation.EAST
        elif new_orientation == Orientation.EAST:
            self.set_action("TURN_RIGHT", self.get_turn())
            self.scan.orientation = Orientation.SOUTH
        elif new_orientation == Orientation.WEST:
            self.set_action("TURN_LEFT", self.get_turn())
            self.scan.orientation = Orientation.NORTH

    def fire(self):
        self.set_action("FIRE", self.get_turn())
        
    def set_action(self, action_str, turn):
        print(f"Setting action: {action_str} for turn {turn}")
        requests.post(f"http://127.0.0.1:5000/action",json={"action": action_str, "turn": turn, "color": self.color})