
# mini_twitter app file

from flask import Flask

app = Flask(__name__)

@app.route("/ping", method=['GET'])
def ping() :
    return "pong"

