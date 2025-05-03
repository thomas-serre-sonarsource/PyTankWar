import pygame
import enum 

class Action(enum.Enum):
    FORWARD = 1 
    BACKWARD = 2

class Tank:

    def __init__(self):
        self.next_action = None 
        self.x = 10
        self.y = 10

    def set_next_action(self, action):
        self.next_action = action        
