
import time
from tankwar.logic.arena import Arena
from tankwar.logic.game_cleaner import GameCleaner
from tankwar.logic.game_writer import GameWriter
from tankwar.logic.missile_collider import MissileCollider
from tankwar.logic.missile_updater import MissileUpdater
from tankwar.logic.tank import Tank
from tankwar.logic.tank_actioner import TankActioner
from tankwar.logic.tank_mover import TankMover
from tankwar.logic.tank_updater import TankUpdater

class Game:
    
    def __init__(self):
        self.last_update = time.time()

        self.arena = Arena()

        self.explosions = []

        self.missiles = []
        self.missile_updater = MissileUpdater(self.arena)

        self.tanks = [] 
        self.tanks.append(Tank(5, 5, "green"))
        self.tanks.append(Tank(15, 15, "red"))
        self.tanks.append(Tank(5, 15, "blue"))
        self.tanks.append(Tank(15, 5, "orange"))

        self.tank_mover = TankMover()
        self.tank_updater = TankUpdater(self.arena, self.missiles)
        self.tank_actioner = TankActioner()

        self.missile_collider = MissileCollider(self.missiles, self.tanks, self.explosions)

        self.turn = 0

        self.game_cleaner = GameCleaner()
        self.game_writer = GameWriter()
        

    def update(self, tanks, missiles):
        if time.time() - self.last_update > 1.:
            print("Updating game state...", time.time())
            for tank in tanks:
                self.tank_actioner.read_action(tank, self.turn)
                self.tank_updater.update(tank)
        
            for missile in missiles:
                self.missile_updater.update(missile)
            
            self.missile_collider.collide()
            self.last_update = time.time()
            self.turn += 1
            self.game_writer.write(self)
            self.game_cleaner.clean(self)

        if time.time() - self.last_update > 0.11:
            time.sleep(0.1)

    def run(self):
        while True:
            self.update(self.tanks, self.missiles)

if __name__ == '__main__':
    game = Game().run()