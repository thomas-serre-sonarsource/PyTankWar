import random
import pygame

from arena import Arena
from arena_drawer import ArenaDrawer
from explosion_drawer import ExplosionDrawer
from missile_collider import MissileCollider
from missile_drawer import MissileDrawer
from missile_updater import MissileUpdater
from tank import Tank, Action
from tank_actioner import TankActioner
from tank_drawer import TankDrawer
from tank_mover import TankMover
from tank_updater import TankUpdater

pygame.init()

class Game:
    
    def __init__(self):
        self.last_update = pygame.time.get_ticks()
        self.window = pygame.display.set_mode((800, 600))

        self.arena = Arena()
        self.arena_drawer = ArenaDrawer()

        self.explosions = []
        self.explosion_drawer = ExplosionDrawer()

        self.missiles = []
        self.missile_updater = MissileUpdater(self.arena)
        self.missile_drawer = MissileDrawer()


        self.tanks = [] 
        self.tanks.append(Tank(5, 5, "green"))
        self.tanks.append(Tank(15, 15, "red"))
        self.tanks.append(Tank(5, 15, "blue"))
        self.tanks.append(Tank(15, 5, "orange"))

        self.tank_drawer = TankDrawer()
        self.tank_mover = TankMover()
        self.tank_updater = TankUpdater(self.arena, self.missiles)
        self.tank_actioner = TankActioner()

        self.missile_collider = MissileCollider(self.missiles, self.tanks, self.explosions)

    def update(self, tanks, missiles):
        if pygame.time.get_ticks() - self.last_update > 1000:
            for tank in tanks:
                self.tank_actioner.read_action(tank)
                self.tank_updater.update(tank)
        
            for missile in missiles:
                self.missile_updater.update(missile)
            
            self.missile_collider.collide()
            self.last_update = pygame.time.get_ticks()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.update(self.tanks, self.missiles)

            self.window.fill((0, 0, 0))
            self.arena_drawer.draw(self.arena, self.window)
            for tank in self.tanks:
                self.tank_drawer.draw(self.window, self.arena_drawer, tank)
            for missile in self.missiles:
                self.missile_drawer.draw(self.window, self.arena_drawer, missile)
            for explosion in self.explosions:
                self.explosion_drawer.draw(self.window, self.arena_drawer, explosion)

            pygame.display.flip()

if __name__ == '__main__':
    game = Game().run()