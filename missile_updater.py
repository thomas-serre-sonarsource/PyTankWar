from arena import Arena
from missile import Missile
from missile_mover import MissileMover
from tank import Action, Tank
import pygame

class MissileUpdater:

    def __init__(self, arena: Arena):
        self.arena = arena  
        self.missile_mover = MissileMover()

    def update(self, missile: Missile):
        self.missile_mover.move_forward(missile, self.arena) 
    