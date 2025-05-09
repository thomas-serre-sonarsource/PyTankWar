import enum

from tankwar.logic.orientation import Orientation 

class Action(enum.Enum):
    FORWARD = 1 
    BACKWARD = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    TURN_TURRET_LEFT = 5 
    TURN_TURRET_RIGHT = 6 
    FIRE = 7
    SCAN = 8

class Tank:

    def __init__(self, x:int, y:int, color:str, orientation:Orientation = Orientation.NORTH, turret_orientation:Orientation = Orientation.NORTH):
        self.next_action = None 
        self.x = x
        self.y = y
        self.orientation = orientation
        self.turret_orientation = turret_orientation
        self.color = color

    def set_next_action(self, action):
        self.next_action = action        
