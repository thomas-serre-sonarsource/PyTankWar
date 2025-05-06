import json
import time
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return {"message": "Hello World"}

@app.route("/<color>/<action>")
def set_action(color, action):
    with open(f"{color}_action.txt", "w") as f:
        f.write(action)
    return {"message": f"Action {action} for {color} set."}

@app.route("/turn")
def get_turn():
    try :
        with open("game.json", "r") as f:
            content = f.read()
        json_dict = json.loads(content)
    except json.JSONDecodeError as e:
        with open("game.json", "r") as f:
            content = f.read()
            json_dict = json.loads(content)
    return str(json_dict["turn"])

@app.route("/status")
def get_game_status():
    print("Fetching game status...", time.time())
    with open("game.json", "r") as f:
        content = f.read()
    print("Game status fetched.", time.time())
    return content

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)
