import pygame

from tankwar.logic.arena import Arena 

class ArenaDrawer:
    def __init__(self):
        self.cell_size_in_pixels = 20

    def draw(self, arena: Arena, window : pygame.Surface):
        for row in range(arena.cell_per_row):
            for col in range(arena.cell_per_col):
                x = col * self.cell_size_in_pixels
                y = row * self.cell_size_in_pixels

                pygame.draw.rect(window, (255, 255, 255), (x+1, y+1, self.cell_size_in_pixels-2, self.cell_size_in_pixels-2), 0)