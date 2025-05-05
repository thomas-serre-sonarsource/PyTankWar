import enum

from orientation import Orientation 

class Action(enum.Enum):
    FORWARD = 1 
    BACKWARD = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    TURN_TURRET_LEFT = 5 
    TURN_TURRET_RIGHT = 6 
    FIRE = 7

class Tank:

    def __init__(self, x:int, y:int, color:str):
        self.next_action = None 
        self.x = x
        self.y = y
        self.orientation = Orientation.NORTH
        self.turret_orientation = Orientation.NORTH
        self.color = color

    def set_next_action(self, action):
        self.next_action = action        
