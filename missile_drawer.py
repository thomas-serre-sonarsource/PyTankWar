from arena_drawer import ArenaDrawer
from missile import Missile
from orientation import Orientation
import pygame

class MissileDrawer:

    def __init__(self):
        missile_image = pygame.image.load("green_missile.png")   

        self.missile_image_per_orientation = {}
        self.missile_image_per_orientation[Orientation.NORTH] = missile_image
        self.missile_image_per_orientation[Orientation.SOUTH] = pygame.transform.flip(missile_image, False, True)
        self.missile_image_per_orientation[Orientation.EAST] = pygame.transform.rotate(missile_image, -90)
        self.missile_image_per_orientation[Orientation.WEST] = pygame.transform.rotate(missile_image, +90)

    def draw(self, window, arena_drawer : ArenaDrawer, missile: Missile):
        window.blit(self.missile_image_per_orientation[missile.orientation], (missile.x * arena_drawer.cell_size_in_pixels, missile.y * arena_drawer.cell_size_in_pixels))