from tank import Action, Tank
import os

class TankActioner:

    def read_action(self, tank: Tank):
        if( not os.path.exists(f"{tank.color}_action.txt")):
            return 
        with open(f"{tank.color}_action.txt", "r") as file:
            action = file.read().strip()
            if action == "FORWARD":
                tank.next_action = Action.FORWARD
            elif action == "BACKWARD":
                tank.next_action = Action.BACKWARD
            elif action == "TURN_LEFT":
                tank.next_action = Action.TURN_LEFT
            elif action == "TURN_RIGHT":
                tank.next_action = Action.TURN_RIGHT
            elif action == "TURN_TURRET_LEFT":
                tank.next_action = Action.TURN_TURRET_LEFT
            elif action == "TURN_TURRET_RIGHT":
                tank.next_action = Action.TURN_TURRET_RIGHT
            elif action == "FIRE":
                tank.next_action = Action.FIRE
            else:
                tank.next_action = None