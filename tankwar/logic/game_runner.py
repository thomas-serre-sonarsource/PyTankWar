import json
import enum 

class GameStatus(enum.Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    RESET = "RESET"

class GameRunner:

    def pause(self):   
        with open("game_status.txt", "w") as file:
            file.write(GameStatus.PAUSED.value)
    
    def is_running(self):
        try:
            with open("game_status.txt", "r") as file:
                content = file.read()
            if content.strip() == GameStatus.RUNNING.value:
                return True
            return False
        except FileNotFoundError:
            return False
        
    def is_reset(self):
        try:
            with open("game_status.txt", "r") as file:
                content = file.read()
            print(content.strip())
            if content.strip() == GameStatus.RESET.value:
                return True
            return False
        except FileNotFoundError:
            return False