import pygame

from arena_drawer import ArenaDrawer
from tankwar.logic.explosion import Explosion
from tankwar.drawer.images import IMAGE_PATH

class ExplosionDrawer:

    def __init__(self):
        self.image = pygame.image.load(IMAGE_PATH.joinpath("explosion.png"))

    def draw(self, window, arena_drawer : ArenaDrawer, explosion: Explosion):
        window.blit(self.image, (explosion.x * arena_drawer.cell_size_in_pixels, explosion.y * arena_drawer.cell_size_in_pixels))