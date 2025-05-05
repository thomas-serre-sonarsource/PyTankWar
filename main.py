import random
import pygame

from arena import Arena
from arena_drawer import ArenaDrawer
from missile_drawer import MissileDrawer
from missile_updater import MissileUpdater
from tank import Tank, Action
from tank_drawer import TankDrawer
from tank_mover import TankMover
from tank_updater import TankUpdater

last_update = pygame.time.get_ticks()
def update(tanks, missiles):
    global last_update
    if pygame.time.get_ticks() - last_update > 1000:
        for tank in tanks:
            tank.next_action = random.choice(list(Action))
            print(tank.next_action)
            tank_updater.update(tank)
    
        for missile in missiles:
            missile_updater.update(missile)

        last_update = pygame.time.get_ticks()

pygame.init()

window = pygame.display.set_mode((800, 600))

arena = Arena()
arena_drawer = ArenaDrawer()

missiles = []
missile_updater = MissileUpdater(arena)
missile_drawer = MissileDrawer()

tanks = [] 
tanks.append(Tank(5, 10, "green"))
tanks.append(Tank(15, 10, "red"))

tank_drawer = TankDrawer()
tank_mover = TankMover()
tank_updater = TankUpdater(arena, missiles)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    update(tanks, missiles)

    window.fill((0, 0, 0))
    arena_drawer.draw(arena, window)
    for tank in tanks:
        tank_drawer.draw(window, arena_drawer, tank)
    for missile in missiles:
        missile_drawer.draw(window, arena_drawer, missile)

    pygame.display.flip()

