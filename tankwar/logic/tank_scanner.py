import json
import math
from tankwar.logic.arena import Arena
from tankwar.logic.missile import Missile
from tankwar.logic.tank import Tank
from tankwar.logic.target import Target

class ScanResult:
    def __init__(self, 
                 turn:int, 
                 x: int, 
                 y: int, 
                 color: str, 
                 orientation: str, 
                 turret_orientation: str, 
                 target_x: int, 
                 target_y: int,
                 missiles: list[Missile],
                 tanks: list[Tank]                 
                 ):
        self.turn = turn 
        self.x = x
        self.y = y
        self.color = color
        self.orientation = orientation
        self.turret_orientation = turret_orientation
        self.target_x = target_x
        self.target_y = target_y
        self.missiles = missiles
        self.tanks = tanks

    def to_json(self):
        json_dict = {
            "turn": self.turn,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "orientation": self.orientation.value,
            "turret_orientation": self.turret_orientation.value,
            "target_x": self.target_x,
            "target_y": self.target_y,
            "missiles": [
                {
                    "x": missile.x,
                    "y": missile.y,
                    "color": missile.color,
                    "orientation": missile.orientation.value,
                } for missile in self.missiles
            ],
            "tanks": [
                {
                    "x": tank.x,
                    "y": tank.y,
                    "color": tank.color,
                    "orientation": tank.orientation.value,
                    "turret_orientation": tank.turret_orientation.value,
                } for tank in self.tanks
            ],
        }
        return json.dumps(json_dict)
    
class TankScanner:

    def __init__(self, arena: Arena, missiles: list[Missile], tanks: list[Tank], targets: list[Target]):
        self.arena = arena  
        self.missiles = missiles
        self.tanks = tanks
        self.targets = targets

    def scan(self, turn : int, tank: Tank):
        target = [target for target in self.targets if target.color == tank.color][0]
        missiles = [missile for missile in self.missiles if math.sqrt((missile.x - tank.x)**2 + (missile.y - tank.y)**2) <= 10]
        tanks = [t for t in self.tanks if 0.1 <= math.sqrt((t.x - tank.x)**2 + (t.y - tank.y)**2) <= 10]
        scan = ScanResult(turn, tank.x, tank.y, tank.color, tank.orientation, tank.turret_orientation, target.x, target.y, missiles, tanks)
        with open(f"{tank.color}_scan.txt", "w") as f:
            f.write(scan.to_json())
        print(f"Tank {tank.color} scanned at turn {turn}: {scan.to_json()}")