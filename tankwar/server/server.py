import json
import time
from flask import Flask, request, jsonify

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
    data = request.get_json()

    with open(f"{color}_action.txt", "r") as f:
        action = f.read()

    return jsonify({
        'action': action,
        'color': color
    })

@app.route("/turn")
def get_turn():
    try :
        with open("game.json", "r") as f:
            content = f.read()
        json_dict = json.loads(content)
    except json.JSONDecodeError:
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
