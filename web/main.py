import json
from flask import Flask, request


# web server for debug
app = Flask(__name__)

@app.route("/")
def index():
    return "this is index"

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=6000)