from tankwar.logic.arena import Arena
from tankwar.logic.missile import Missile
from tankwar.logic.tank import Tank

class TankFirer:

    def __init__(self, arena: Arena, missiles: list[Missile]):
        self.arena = arena  
        self.missiles = missiles

    def fire(self, tank: Tank):
        missile = Missile(tank.x, tank.y, tank.turret_orientation, tank.color)
        self.missiles.append(missile)