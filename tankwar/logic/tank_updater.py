from tankwar.logic.arena import Arena
from tankwar.logic.missile import Missile
from tankwar.logic.tank import Action, Tank

from tankwar.logic.tank_firer import TankFirer
from tankwar.logic.tank_mover import TankMover

class TankUpdater:

    def __init__(self, arena: Arena, missiles: list[Missile]):
        self.arena = arena  
        self.tank_mover = TankMover()
        self.tank_firer = TankFirer(arena, missiles)

    def update(self, tank: Tank):
        action = tank.next_action
        match action:
            case Action.FORWARD:
                self.tank_mover.move_forward(tank, self.arena) 
            case Action.BACKWARD:
                self.tank_mover.move_backward(tank, self.arena)
            case Action.TURN_LEFT:
                self.tank_mover.turn_tank_left(tank)
            case Action.TURN_RIGHT:
                self.tank_mover.turn_tank_right(tank)
            case Action.TURN_TURRET_LEFT:
                self.tank_mover.turn_turret_left(tank)
            case Action.TURN_TURRET_RIGHT:
                self.tank_mover.turn_turret_right(tank)
            case Action.FIRE:
                self.tank_firer.fire(tank)