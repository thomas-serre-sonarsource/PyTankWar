import json
import time
import pygame
import requests

from tankwar.drawer.target_drawer import TargetDrawer
from tankwar.logic import colors
from tankwar.logic.arena import Arena
from arena_drawer import ArenaDrawer
from tankwar.logic.explosion import Explosion
from explosion_drawer import ExplosionDrawer
from tankwar.logic.missile import Missile
from missile_drawer import MissileDrawer
from tankwar.logic.orientation import Orientation
from tankwar.logic.tank import Tank
from tank_drawer import TankDrawer
from tankwar.logic.target import Target

pygame.init()

class GameDrawer:
    
    def __init__(self):
        self.last_draw = pygame.time.get_ticks()
        self.window = pygame.display.set_mode((1400, 1000))

        self.turn = 0
        self.font = pygame.font.Font(None, 36)

        self.arena = Arena()
        self.arena_drawer = ArenaDrawer()

        self.explosions = []
        self.explosion_drawer = ExplosionDrawer()

        self.missiles = []
        self.missile_drawer = MissileDrawer()

        self.tanks = [] 
        self.tank_drawer = TankDrawer()

        self.targets = []
        self.target_drawer = TargetDrawer()

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
            time.sleep(0.01)

    def read_state(self):
        print("Reading state from server...", time.time())

        r = requests.get("http://127.0.0.1:5000/status")
        print("State downloaded from server...", time.time())
        json_str = r.content.decode("utf-8")
        try :
            json_dict = json.loads(json_str)
        except json.JSONDecodeError:
            print("Error decoding JSON:", json_str)
            return
        self.arena.cell_per_row = json_dict["arena"]["cell_per_row"]
        self.arena.cell_per_col = json_dict["arena"]["cell_per_col"]
        self.tanks = [Tank(tank["x"], tank["y"], tank["color"], Orientation(tank["orientation"]), Orientation(tank["turret_orientation"])) for tank in json_dict["tanks"]]
        self.missiles = [Missile(missile["x"], missile["y"], Orientation(missile["orientation"]), missile["color"]) for missile in json_dict["missiles"]]
        self.explosions = [Explosion(explosion["x"], explosion["y"]) for explosion in json_dict["explosions"]]
        self.targets = [Target(target["x"], target["y"], target["color"]) for target in json_dict["targets"]]
        self.turn = json_dict["turn"]
        self.scores = json_dict["scores"]
        self.game_status = json_dict["status"]
        
        print("Ending reading state from server...", time.time())

    def draw(self):
        self.window.fill((0, 0, 0))
        self.arena_drawer.draw(self.arena, self.window)
        for target in self.targets:
            self.target_drawer.draw(self.window, self.arena_drawer, target)
        for tank in self.tanks:
            self.tank_drawer.draw(self.window, self.arena_drawer, tank)
        for missile in self.missiles:
            self.missile_drawer.draw(self.window, self.arena_drawer, missile)
        for explosion in self.explosions:
            self.explosion_drawer.draw(self.window, self.arena_drawer, explosion)
        
        turn_surface = self.font.render(f"Turn : {self.turn}", True, (255,255,255))
        turn_rect = turn_surface.get_rect()
        turn_rect.topleft = (1050, 50) 
        self.window.blit(turn_surface, turn_rect)

        status_surface = self.font.render(f"Status : {self.game_status}", True, (255,255,255))
        status_rect = turn_surface.get_rect()
        status_rect.topleft = (1050, 75)
        self.window.blit(status_surface, status_rect)

        y0 = 125
        colors_dict = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "orange": (255, 165, 0),
            "black": (64, 64, 64),
            "purple": (128, 0, 128),
            "green": (0, 255, 0),
        }
        
        for color in colors.COLORS:
            tank = [t for t in self.tanks if t.color == color]
            target = [t for t in self.targets if t.color == color]
            
            if len(tank) > 0 and len(target) > 0:
                tank = tank[0]
                target = target[0]
                tank_surface = self.font.render(f"{color} tank : x : {tank.x}, y : {tank.y}", True, colors_dict[color])
                tank_rect = tank_surface.get_rect()
                tank_rect.topleft = (1050, y0)  
                self.window.blit(tank_surface, tank_rect) 
                
                target_surface = self.font.render(f"{color} target: x : {target.x}, y : {target.y}", True, colors_dict[color])
                target_rect = target_surface.get_rect()
                target_rect.topleft = (1050, y0+25)
                self.window.blit(target_surface, target_rect) 
                
                score_surface = self.font.render(f"{color} score: {self.scores[color]}", True, colors_dict[color])
                score_rect = score_surface.get_rect()
                score_rect.topleft = (1050, y0+50)
                self.window.blit(score_surface, score_rect) 
            
            y0 += 100
        pygame.display.flip()

if __name__ == '__main__':
    game = GameDrawer().run()