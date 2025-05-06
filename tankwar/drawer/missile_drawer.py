from tankwar.logic.colors import COLORS
from arena_drawer import ArenaDrawer
from tankwar.logic.missile import Missile
from tankwar.logic.orientation import Orientation
from tankwar.drawer.images import IMAGE_PATH

import pygame

class MissileDrawer:

    def __init__(self):
        images_per_color = {}
        for color in COLORS:
            images_per_color[color] = pygame.image.load(IMAGE_PATH.joinpath(f"{color}_missile.png"))

        self.missile_image_per_color_and_orientation = {}
        for color in COLORS:
            missile_image = images_per_color[color]
            
            self.missile_image_per_color_and_orientation[(color, Orientation.NORTH)] = missile_image
            self.missile_image_per_color_and_orientation[(color, Orientation.SOUTH)] = pygame.transform.flip(missile_image, False, True)
            self.missile_image_per_color_and_orientation[(color, Orientation.EAST)] = pygame.transform.rotate(missile_image, -90)
            self.missile_image_per_color_and_orientation[(color, Orientation.WEST)] = pygame.transform.rotate(missile_image, +90)

    def draw(self, window, arena_drawer : ArenaDrawer, missile: Missile):
        window.blit(self.missile_image_per_color_and_orientation[(missile.color, missile.orientation)], (missile.x * arena_drawer.cell_size_in_pixels, missile.y * arena_drawer.cell_size_in_pixels))