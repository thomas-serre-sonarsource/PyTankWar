import random
import time
import requests


class OrangePlayer:
    def __init__(self):
        self.color = "orange"
        self.last_turn = None

    def get_turn(self):
        response = requests.get("http://127.0.0.1:5000/turn")
        return int(response.content.decode("utf-8"))
    
    def play(self):
        current_turn = self.get_turn()
        if current_turn == self.last_turn:
            time.sleep(0.1)
            return 
        self.last_turn = current_turn
        random_action = random.choice([
                #"FORWARD",
                #"BACKWARD",
                "TURN_LEFT",
                #"TURN_RIGHT",
                #"TURN_TURRET_LEFT",
                #"TURN_TURRET_RIGHT",
                #"FIRE",
                #"SCAN"
            ])
        
        print(f"AI {self.color} is playing turn {current_turn} with action {random_action}")
        self.set_action(random_action, current_turn)
        
    def set_action(self, action_str, turn):
        requests.post(f"http://127.0.0.1:5000/action",json={"action": action_str, "turn": turn, "color": self.color})            