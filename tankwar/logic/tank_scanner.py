import json
from tankwar.logic.arena import Arena
from tankwar.logic.missile import Missile
from tankwar.logic.tank import Tank

class ScanResult:
    def __init__(self, turn:int, x: int, y: int, color: str, orientation: str, turret_orientation: str):
        self.turn = turn 
        self.x = x
        self.y = y
        self.color = color
        self.orientation = orientation
        self.turret_orientation = turret_orientation

    def to_json(self):
        json_dict = {
            "turn": self.turn,
            "x": self.x,
            "y": self.y,
            "color": self.color,
            "orientation": self.orientation.value,
            "turret_orientation": self.turret_orientation.value
        }
        return json.dumps(json_dict)
    
class TankScanner:

    def __init__(self, arena: Arena, missiles: list[Missile], tanks: list[Tank]):
        self.arena = arena  
        self.missiles = missiles
        self.tanks = tanks

    def scan(self, turn : int, tank: Tank):
        scan = ScanResult(turn, tank.x, tank.y, tank.color, tank.orientation, tank.turret_orientation)
        with open(f"{tank.color}_scan.txt", "w") as f:
            f.write(scan.to_json())
        print(f"Tank {tank.color} scanned at turn {turn}: {scan.to_json()}")