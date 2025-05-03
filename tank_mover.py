from arena import Arena
from tank import Tank

class TankMover:

    def move_backward(self, tank: Tank, arena: Arena):
        tank.y += 1
        if tank.y == arena.cell_per_col:
            tank.y = 0

    def move_forward(self, tank: Tank, arena: Arena):
        tank.y -= 1
        if tank.y == -1:
            tank.y = arena.cell_per_col - 1