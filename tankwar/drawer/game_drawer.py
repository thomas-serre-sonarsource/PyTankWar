import json
import time
import pygame
import requests

from tankwar.logic.arena import Arena
from arena_drawer import ArenaDrawer
from tankwar.logic.explosion import Explosion
from explosion_drawer import ExplosionDrawer
from tankwar.logic.game_writer import GameWriter
from tankwar.logic.missile import Missile
from tankwar.logic.missile_collider import MissileCollider
from missile_drawer import MissileDrawer
from tankwar.logic.orientation import Orientation
from tankwar.logic.tank import Tank
from tankwar.logic.tank_actioner import TankActioner
from tank_drawer import TankDrawer
from tankwar.logic.tank_mover import TankMover
from tankwar.logic.tank_updater import TankUpdater

pygame.init()

class GameDrawer:
    
    def __init__(self):
        self.last_draw = pygame.time.get_ticks()
        self.window = pygame.display.set_mode((800, 600))

        self.arena = Arena()
        self.arena_drawer = ArenaDrawer()

        self.explosions = []
        self.explosion_drawer = ExplosionDrawer()

        self.missiles = []
        self.missile_drawer = MissileDrawer()

        self.tanks = [] 
        self.tank_drawer = TankDrawer()
        self.tank_mover = TankMover()
        self.tank_updater = TankUpdater(self.arena, self.missiles)
        self.tank_actioner = TankActioner()

        self.missile_collider = MissileCollider(self.missiles, self.tanks, self.explosions)

        self.game_writer = GameWriter()


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if pygame.time.get_ticks() - self.last_draw > 250:
                self.read_state()
                self.draw()
                self.last_draw = pygame.time.get_ticks()
                
    def read_state(self):
        print("Reading state from server...", time.time())

        r = requests.get("http://127.0.0.1:5000/status")
        print("State downloaded from server...", time.time())
        json_str = r.content.decode("utf-8")
        json_dict = json.loads(json_str)
        self.arena.cell_per_row = json_dict["arena"]["cell_per_row"]
        self.arena.cell_per_col = json_dict["arena"]["cell_per_col"]
        self.tanks = [Tank(tank["x"], tank["y"], tank["color"], Orientation(tank["orientation"]), Orientation(tank["turret_orientation"])) for tank in json_dict["tanks"]]
        self.missiles = [Missile(missile["x"], missile["y"], Orientation(missile["orientation"]), missile["color"]) for missile in json_dict["missiles"]]
        self.explosions = [Explosion(explosion["x"], explosion["y"]) for explosion in json_dict["explosions"]]
        print("Ending reading state from server...", time.time())

    def draw(self):
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
    game = GameDrawer().run()