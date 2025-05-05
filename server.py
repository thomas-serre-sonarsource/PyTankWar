from flask import Flask

from game import Game

app = Flask(__name__)

@app.route("/")
def hello():
    return {"message": "Hello World"}

@app.route("/<color>/<action>")
def set_action(color, action):
    with open(f"{color}_action.txt", "w") as f:
        f.write(action)
    return {"message": f"Action {action} for {color} set."}

if __name__ == '__main__':
    app.run(debug=True)
