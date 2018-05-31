#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response, request
from camera_pi import Camera
from AlphaBot import AlphaBot

app = Flask(__name__)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

Camera = Camera()

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shot')
def shot():
    pic = Camera().get_frame()

#bot = AlphaBot()
@app.route("/gamepad_data", methods=['POST'])
def gamepad_data():
    data = request.get_json()
    bottons = data['bottons']
    axis = data['axes']
    bot_move = axis[:2]
    bot_move[1] = - bot_move[1]
    camera_move = axis[2:]
    b,a,y,x = bottons[:4]
    u = bot_move[0]+botmove[1]
    v = -bot_move[0]+bot_move[1]
    u /= 2**0.5
    v /= 2**0.5
    bot.setMotor(u, v)

    return Response("receive")

@app.route('/gamepad_test')
def gamepad_test():
    return render_template('gamepad.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
