import os 
class GameCleaner:
    
    def clean(self, game:"Game"):
        turn = game.turn
        txt_files = [f for f in os.listdir(".") if "_action_" in f and f.endswith(".txt")]
        for filename in txt_files:
            _, _, raw_action_turn = filename.split("_")
            action_turn = raw_action_turn.strip()[:-4]
            if int(action_turn) < turn - 1 or int(action_turn) > turn :
                os.remove(filename)