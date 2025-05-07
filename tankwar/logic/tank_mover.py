from tankwar.logic.arena import Arena
from tankwar.logic.orientation import Orientation
from tankwar.logic.tank import Tank

class TankMover:

    def __init__(self, tanks: list[Tank]):
        self.tanks = tanks

    def move_backward(self, tank: Tank, arena: Arena):
        x0, y0 = tank.x, tank.y
        match tank.orientation:
            case Orientation.NORTH:
                tank.y += 1
            case Orientation.SOUTH:
                tank.y -= 1
            case Orientation.EAST:
                tank.x -= 1
            case Orientation.WEST:
                tank.x += 1
        self.handle_movement_out_of_arena(tank, arena)
        if self.is_collision_with_tank(tank):
            tank.x, tank.y = x0, y0

    def move_forward(self, tank: Tank, arena: Arena):
        x0, y0 = tank.x, tank.y
        match tank.orientation:
            case Orientation.NORTH:
                tank.y -= 1
            case Orientation.SOUTH:
                tank.y += 1
            case Orientation.EAST:
                tank.x += 1
            case Orientation.WEST:
                tank.x -= 1
        self.handle_movement_out_of_arena(tank, arena)
        if self.is_collision_with_tank(tank):
            tank.x, tank.y = x0, y0

    def is_collision_with_tank(self, tank: Tank):
        for other_tank in self.tanks:
            if tank != other_tank and tank.x == other_tank.x and tank.y == other_tank.y:
                return True 
        return False 
      
    def handle_movement_out_of_arena(self, tank: Tank, arena: Arena):
        if tank.y == -1:
            tank.y = arena.cell_per_col - 1
        if tank.y == arena.cell_per_col:
            tank.y = 0
        if tank.x == -1:
            tank.x = arena.cell_per_row - 1
        if tank.x == arena.cell_per_row:
            tank.x = 0
        
    def turn_tank_left(self, tank: Tank):
        tank.orientation = self.turn_left(tank.orientation)

    def turn_tank_right(self, tank: Tank):
        tank.orientation = self.turn_right(tank.orientation)

    def turn_turret_left(self, tank: Tank):
        tank.turret_orientation = self.turn_left(tank.turret_orientation)

    def turn_turret_right(self, tank: Tank):
        tank.turret_orientation = self.turn_right(tank.turret_orientation)

    def turn_right(self, orientation: Orientation):
        if orientation.value - 1 == 0 :
            return Orientation.EAST
        return Orientation(orientation.value - 1)

    def turn_left(self, orientation: Orientation):
        if orientation.value + 1 == 5:
            return  Orientation.NORTH
        return Orientation(orientation.value + 1)