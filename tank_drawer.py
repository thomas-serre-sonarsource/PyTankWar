from arena_drawer import ArenaDrawer
from tank import Tank, Orientation
import pygame

class TankDrawer:

    def __init__(self):
        body_image = pygame.image.load("green_tank_body.png")   

        self.body_image_per_orientation = {}
        self.body_image_per_orientation[Orientation.NORTH] = body_image
        self.body_image_per_orientation[Orientation.SOUTH] = pygame.transform.flip(body_image, False, True)
        self.body_image_per_orientation[Orientation.EAST] = pygame.transform.rotate(body_image, -90)
        self.body_image_per_orientation[Orientation.WEST] = pygame.transform.rotate(body_image, +90)
        self.turret_image = pygame.image.load("green_tank_turret.png")

    def draw(self, window, arena_drawer : ArenaDrawer, tank: Tank):
        window.blit(self.body_image_per_orientation[tank.orientation], (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))
        window.blit(self.turret_image, (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))