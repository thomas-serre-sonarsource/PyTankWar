from orientation import Orientation

class Missile:

    def __init__(self, x:int, y:int, orientation:Orientation):
        self.next_action = None 
        self.x = x
        self.y = y
        self.orientation = orientation