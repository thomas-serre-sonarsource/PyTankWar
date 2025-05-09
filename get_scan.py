import requests

for color in ["red", "blue", "orange", "green"]:
    print(requests.get(f"http://127.0.0.1:5000/scan/{color}").content.decode("utf-8"))
