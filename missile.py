from orientation import Orientation

class Missile:

    def __init__(self, x:int, y:int, orientation:Orientation, color:str):
        self.next_action = None 
        self.x = x
        self.y = y
        self.color = color
        self.orientation = orientation