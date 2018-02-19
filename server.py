from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/live")
def live():
    return "Will return the live stream from the camera..."