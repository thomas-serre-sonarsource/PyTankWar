from arena import Arena
from arena_drawer import ArenaDrawer
from tank import Tank
import pygame

class TankDrawer:

    def __init__(self):
        self.body_image = pygame.image.load("green_tank_body.png")        
        self.turret_image = pygame.image.load("green_tank_turret.png")

    def draw(self, window, arena_drawer : ArenaDrawer, tank: Tank):
        window.blit(self.body_image, (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))
        window.blit(self.turret_image, (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))