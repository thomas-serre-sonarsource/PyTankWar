from tankwar.logic.arena import Arena
from tankwar.logic.missile import Missile
from tankwar.logic.missile_mover import MissileMover

class MissileUpdater:

    def __init__(self, arena: Arena):
        self.arena = arena  
        self.missile_mover = MissileMover()

    def update(self, missile: Missile):
        self.missile_mover.move_forward(missile, self.arena) 
    