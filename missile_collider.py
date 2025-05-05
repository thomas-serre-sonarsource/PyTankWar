from explosion import Explosion
from missile import Missile
from tank import Tank

class MissileCollider:

    def __init__(self, missiles: list[Missile], tanks: list[Tank], explosions):
        self.missiles = missiles
        self.explosions = explosions
        self.tanks = tanks  

    def collide(self):
        self.explosions.clear()

        missiles_to_remove = set()
        tanks_to_remove = set()

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
        
        for missile in missiles_to_remove:
            self.missiles.remove(missile)
        for tank in tanks_to_remove:
            self.tanks.remove(tank)