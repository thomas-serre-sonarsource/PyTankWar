import random
from tankwar.logic.arena import Arena
from tankwar.logic.explosion import Explosion
from tankwar.logic.missile import Missile
from tankwar.logic.tank import Tank
from tankwar.logic.target import Target

class MissileCollider:

    def __init__(self, arena: Arena, missiles: list[Missile], tanks: list[Tank], explosions, targets: list[Target], scores: dict[str, int]):
        self.missiles = missiles
        self.explosions = explosions
        self.tanks = tanks  
        self.scores = scores
        self.targets = targets
        self.arena = arena

    def collide(self):
        self.explosions.clear()

        missiles_to_remove = set()
        tanks_to_remove = set()
        targets_to_remove = set()

        for i in range(0, len(self.missiles)):
            for j in range(i + 1, len(self.missiles)):
                m1, m2 = self.missiles[i], self.missiles[j]
                if m1.x == m2.x and m1.y == m2.y:
                    missiles_to_remove.add(m1)
                    missiles_to_remove.add(m2)
                    self.explosions.append(Explosion(m1.x, m1.y))
                    break

        for i in range(0, len(self.missiles)):
            for j in range(0, len(self.tanks)):
                m, t = self.missiles[i], self.tanks[j]
                if m.x == t.x and m.y == t.y:
                    missiles_to_remove.add(m)
                    tanks_to_remove.add(t)
                    self.explosions.append(Explosion(m.x, m.y))
                    break

        for i in range(0, len(self.missiles)):
            for j in range(0, len(self.targets)):
                m, t = self.missiles[i], self.targets[j]
                if m.x == t.x and m.y == t.y and m.color == t.color:
                    missiles_to_remove.add(m)
                    targets_to_remove.add(t)
                    self.explosions.append(Explosion(m.x, m.y))
                    break
                
        for target in targets_to_remove:
            self.targets.remove(target)
            self.scores[target.color] += 1
            x, y = None, None
            while True:
                x = random.randint(0, self.arena.cell_per_row - 1)
                y = random.randint(0, self.arena.cell_per_col - 1)
                if not any(t.x == x and t.y == y for t in self.tanks) and not any(t.x == x and t.y == y for t in self.targets):
                    break  
            self.targets.append(Target(x, y, target.color)) 
        
        for missile in missiles_to_remove:
            self.missiles.remove(missile)
        for tank in tanks_to_remove:
            self.tanks.remove(tank)