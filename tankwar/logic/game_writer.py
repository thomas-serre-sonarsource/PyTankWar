import json

class GameWriter:
    
    def write(self, game:"Game"):
        json_dict = {
            "status": game.game_runner.get_status(),
            "turn": game.turn,
            "arena": {
                "cell_per_row": game.arena.cell_per_row,
                "cell_per_col": game.arena.cell_per_col
            },
            "tanks": [
                {
                    "x": tank.x,
                    "y": tank.y,
                    "color": tank.color,
                    "orientation": tank.orientation.value,
                    "turret_orientation": tank.turret_orientation.value,
                } for tank in game.tanks
            ],
            "missiles": [
                {
                    "x": missile.x,
                    "y": missile.y,
                    "color": missile.color,
                    "orientation": missile.orientation.value,
                } for missile in game.missiles
            ],
            "explosions": [
                {
                    "x": explosion.x,
                    "y": explosion.y,
                } for explosion in game.explosions
            ],
            "targets": [
                {
                    "x": target.x,
                    "y": target.y,
                    "color": target.color,
                } for target in game.targets
            ], 
            "scores": game.scores,
        }
        with open("game.json", "w") as file:
            file.write(json.dumps(json_dict, indent=4))