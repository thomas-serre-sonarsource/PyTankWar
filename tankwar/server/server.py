import json
import time
from flask import Flask, request, jsonify

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route("/")
def hello():
    return {"message": "Hello World"}

@app.route('/action', methods=['POST'])
def set_action():
    data = request.get_json()

    action = data.get('action')
    turn = data.get('turn')
    color = data.get('color')

    if not action or not turn or not color:
        return jsonify({'error': 'action, turn and color fields are required'}), 400

    with open(f"{color}_action_{turn}.txt", "w") as f:
        f.write(action)

    return jsonify({
        'action': action,
        'turn': turn, 
        'color': color
    })


@app.route('/action/<color>', methods=['GET'])
def get_action(color):
    with open(f"{color}_action.txt", "r") as f:
        action = f.read()

    return jsonify({
        'action': action,
        'color': color
    })

@app.route('/scan/<color>', methods=['GET'])
def get_scan(color):
    try :
        with open(f"{color}_scan.txt", "r") as f:
            scan = f.read()
        return jsonify({
            "scan": scan,
            "color": color
        })
    except FileNotFoundError:
        return jsonify({})

@app.route("/turn")
def get_turn():
    try :
        with open("game.json", "r") as f:
            content = f.read()
        json_dict = json.loads(content)
    except json.JSONDecodeError:
        time.sleep(0.01)
        with open("game.json", "r") as f:
            content = f.read()
            json_dict = json.loads(content)
    return str(json_dict["turn"])

@app.route("/status")
def get_game_status():
    with open("game.json", "r") as f:
        content = f.read()
    return content

@app.route("/game/pause", methods=["POST"])
def pause_game():
    with open("game_status.txt", "w") as file:
        file.write("PAUSED")
    return jsonify({"status": "Game paused"})

@app.route("/game/run", methods=["POST"])
def run_game():
    with open("game_status.txt", "w") as file:
        file.write("RUNNING")
    return jsonify({"status": "Game running"})

@app.route("/game/reset", methods=["POST"])
def reset_game():
    with open("game_status.txt", "w") as file:
        file.write("RESET")
    return jsonify({"status": "Game reset"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True)
