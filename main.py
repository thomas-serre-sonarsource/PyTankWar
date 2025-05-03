import pygame

from arena import Arena
from arena_drawer import ArenaDrawer
from tank import Tank, Action
from tank_drawer import TankDrawer
from tank_mover import TankMover
from tank_updater import TankUpdater

pygame.init()

window = pygame.display.set_mode((800, 600))

tank_mover = TankMover()

arena = Arena()
arena_drawer = ArenaDrawer()

tank = Tank()
tank_drawer = TankDrawer()
tank_updater = TankUpdater(arena)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    tank.set_next_action(Action.FORWARD)

    tank_updater.update(tank)

    window.fill((0, 0, 0))
    arena_drawer.draw(arena, window)
    tank_drawer.draw(window, arena_drawer, tank)
    
    pygame.display.flip()