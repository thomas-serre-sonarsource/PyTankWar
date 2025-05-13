from tankwar.logic.colors import COLORS
from arena_drawer import ArenaDrawer
from tankwar.drawer.images import IMAGE_PATH

import pygame

from tankwar.logic.target import Target

class TargetDrawer:

    def __init__(self):
        self.images_per_color = {}
        for color in COLORS:
            self.images_per_color[color] = pygame.image.load(IMAGE_PATH.joinpath(f"{color}_target.png"))

    def draw(self, window, arena_drawer : ArenaDrawer, target: Target):
        window.blit(self.images_per_color[target.color], (target.x * arena_drawer.cell_size_in_pixels, target.y * arena_drawer.cell_size_in_pixels))