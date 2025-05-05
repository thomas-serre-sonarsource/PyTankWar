from arena import Arena
from tank import Orientation, Tank

class TankMover:

    def move_backward(self, tank: Tank, arena: Arena):
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

    def move_forward(self, tank: Tank, arena: Arena):
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
        
    def handle_movement_out_of_arena(self, tank: Tank, arena: Arena):
        if tank.y == -1:
            tank.y = arena.cell_per_col - 1
        if tank.y == arena.cell_per_col:
            tank.y = 0
        if tank.x == -1:
            tank.x = arena.cell_per_row - 1
        if tank.x == arena.cell_per_row:
            tank.x = 0
        
    def turn_left(self, tank: Tank):
        if tank.orientation.value + 1 == 5:
            tank.orientation = Orientation.NORTH
        else:
            tank.orientation = Orientation(tank.orientation.value + 1)

    def turn_right(self, tank: Tank):
        if tank.orientation.value - 1 == 0 :
            tank.orientation = Orientation.EAST
        else:
            tank.orientation = Orientation(tank.orientation.value - 1)