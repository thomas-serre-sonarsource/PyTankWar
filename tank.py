import enum 

class Action(enum.Enum):
    FORWARD = 1 
    BACKWARD = 2
    TURN_LEFT = 3
    TURN_RIGHT = 4
    TURN_TURRET_LEFT = 5 
    TURN_TURRET_RIGHT = 6 
    
class Orientation(enum.Enum):
    NORTH = 1
    WEST = 2
    SOUTH = 3
    EAST = 4

class Tank:

    def __init__(self):
        self.next_action = None 
        self.x = 10
        self.y = 10
        self.orientation = Orientation.NORTH
        self.turret_orientation = Orientation.NORTH

    def set_next_action(self, action):
        self.next_action = action        
