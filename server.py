import os
from stat import S_ISREG, ST_CTIME, ST_MODE

from flask import Flask, send_file

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/live")
def last_image():
    dir_path = os.path.join(os.getcwd(), 'images')

    # all entries in the directory w/ stats
    data = (os.path.join(dir_path, fn) for fn in os.listdir(dir_path))
    data = ((os.stat(path), path) for path in data)

    # regular files, insert creation date
    data = ((stat[ST_CTIME], path)
            for stat, path in data if S_ISREG(stat[ST_MODE]))
    last_created_image = sorted(data, reverse=True)[0]

    if not last_created_image:
        return  "Image not found", 400

    return send_file(os.path.join(dir_path, last_created_image[1]), mimetype='image/jpeg')
