from arena_drawer import ArenaDrawer
from tank import Tank
from orientation import Orientation
import pygame

class TankDrawer:

    def __init__(self):
        body_image = pygame.image.load("green_tank_body.png")   

        self.body_image_per_orientation = {}
        self.body_image_per_orientation[Orientation.NORTH] = body_image
        self.body_image_per_orientation[Orientation.SOUTH] = pygame.transform.flip(body_image, False, True)
        self.body_image_per_orientation[Orientation.EAST] = pygame.transform.rotate(body_image, -90)
        self.body_image_per_orientation[Orientation.WEST] = pygame.transform.rotate(body_image, +90)

        turret_image = pygame.image.load("green_tank_turret.png")
        self.turret_image_per_orientation = {}
        self.turret_image_per_orientation[Orientation.NORTH] = turret_image
        self.turret_image_per_orientation[Orientation.SOUTH] = pygame.transform.flip(turret_image, False, True)
        self.turret_image_per_orientation[Orientation.EAST] = pygame.transform.rotate(turret_image, -90)
        self.turret_image_per_orientation[Orientation.WEST] = pygame.transform.rotate(turret_image, +90)

    def draw(self, window, arena_drawer : ArenaDrawer, tank: Tank):
        window.blit(self.body_image_per_orientation[tank.orientation], (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))
        window.blit(self.turret_image_per_orientation[tank.turret_orientation], (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))