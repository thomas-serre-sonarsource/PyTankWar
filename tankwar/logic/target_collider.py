import random
from tankwar.logic.arena import Arena
from tankwar.logic.tank import Tank
from tankwar.logic.target import Target

class TargetCollider:

    def __init__(self, arena:Arena, targets: list[Target], tanks: list[Tank], scores: dict[str, int]):
        self.targets = targets
        self.tanks = tanks  
        self.arena = arena
        self.scores = scores

    def collide(self):
        
        targets_to_remove = set()

        for i in range(0, len(self.targets)):
            for j in range(0, len(self.tanks)):
                target, tank = self.targets[i], self.tanks[j]
                if target.color == tank.color and target.x == tank.x and tank.y == target.y:
                    targets_to_remove.add(target)
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
            
        