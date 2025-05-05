import pygame

from arena_drawer import ArenaDrawer
from explosion import Explosion
class ExplosionDrawer:

    def __init__(self):
        self.image = pygame.image.load(f"images/explosion.png")

    def draw(self, window, arena_drawer : ArenaDrawer, explosion: Explosion):
        window.blit(self.image, (explosion.x * arena_drawer.cell_size_in_pixels, explosion.y * arena_drawer.cell_size_in_pixels))