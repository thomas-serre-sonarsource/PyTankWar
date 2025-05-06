from tankwar.logic.colors import COLORS
from arena_drawer import ArenaDrawer
from tankwar.logic.tank import Tank
from tankwar.logic.orientation import Orientation
from tankwar.drawer.images import IMAGE_PATH
import pygame

class TankDrawer:

    def __init__(self):
        images_per_color, turret_images_per_color = {}, {}
        for color in COLORS:
            images_per_color[color] = pygame.image.load(IMAGE_PATH.joinpath(f"{color}_tank_body.png"))
            turret_images_per_color[color] = pygame.image.load(IMAGE_PATH.joinpath(f"{color}_tank_turret.png"))

        self.body_image_per_color_and_orientation = {}
        self.turret_image_per_color_and_orientation = {}
        for color in COLORS:
            body_image = images_per_color[color]
            self.body_image_per_color_and_orientation[(color, Orientation.NORTH)] = body_image
            self.body_image_per_color_and_orientation[(color, Orientation.SOUTH)] = pygame.transform.flip(body_image, False, True)
            self.body_image_per_color_and_orientation[(color, Orientation.EAST)] = pygame.transform.rotate(body_image, -90)
            self.body_image_per_color_and_orientation[(color, Orientation.WEST)] = pygame.transform.rotate(body_image, +90)

            turret_image = turret_images_per_color[color]
            self.turret_image_per_color_and_orientation[(color, Orientation.NORTH)] = turret_image
            self.turret_image_per_color_and_orientation[(color, Orientation.SOUTH)] = pygame.transform.flip(turret_image, False, True)
            self.turret_image_per_color_and_orientation[(color, Orientation.EAST)] = pygame.transform.rotate(turret_image, -90)
            self.turret_image_per_color_and_orientation[(color, Orientation.WEST)] = pygame.transform.rotate(turret_image, +90)

    def draw(self, window, arena_drawer : ArenaDrawer, tank: Tank):
        window.blit(self.body_image_per_color_and_orientation[(tank.color, tank.orientation)], (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))
        window.blit(self.turret_image_per_color_and_orientation[(tank.color, tank.turret_orientation)], (tank.x * arena_drawer.cell_size_in_pixels, tank.y * arena_drawer.cell_size_in_pixels))