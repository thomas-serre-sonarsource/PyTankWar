from arena import Arena
from tank import Action, Tank
import pygame

from tank_mover import TankMover

class TankUpdater:

    def __init__(self, arena: Arena):
        self.arena = arena  
        self.tank_mover = TankMover()
        self.last_update = pygame.time.get_ticks() 

    def update(self, tank: Tank):
        if self.last_update + 1000 < pygame.time.get_ticks():
            if tank.next_action is Action.TURN_RIGHT:
                tank.set_next_action(Action.FORWARD)
            else:
                tank.set_next_action(Action.TURN_RIGHT)

            action = tank.next_action
            match action:
                case Action.FORWARD:
                    self.tank_mover.move_forward(tank, self.arena) 
                case Action.BACKWARD:
                    self.tank_mover.move_backward(tank, self.arena)
                case Action.TURN_LEFT:
                    self.tank_mover.turn_left(tank)
                case Action.TURN_RIGHT:
                    self.tank_mover.turn_right(tank)
                    
            self.last_update = pygame.time.get_ticks()