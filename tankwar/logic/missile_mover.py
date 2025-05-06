from tankwar.logic.orientation import Orientation
from tankwar.logic.missile import Missile
from tankwar.logic.arena import Arena

class MissileMover:

    def move_forward(self, missile: Missile, arena: Arena):
        match missile.orientation:
            case Orientation.NORTH:
                missile.y -= 1
            case Orientation.SOUTH:
                missile.y += 1
            case Orientation.EAST:
                missile.x += 1
            case Orientation.WEST:
                missile.x -= 1
        self.handle_movement_out_of_arena(missile, arena)
        
    def handle_movement_out_of_arena(self, missile: Missile, arena: Arena):
        if missile.y == -1:
            missile.y = arena.cell_per_col - 1
        if missile.y == arena.cell_per_col:
            missile.y = 0
        if missile.x == -1:
            missile.x = arena.cell_per_row - 1
        if missile.x == arena.cell_per_row:
            missile.x = 0