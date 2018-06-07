#!/usr/bin/env python
import os
import time
from flask import Flask, render_template, Response, request
from camera_pi import Camera
from AlphaBot import AlphaBot
last = 0

app = Flask(__name__)

@app.route('/')
def index():
	"""Video streaming home page."""
	return render_template('index.html')
def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
			   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
	return Response(gen(Camera()),
					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/shot')
def shot():
	pic = Camera().get_frame()

bot = AlphaBot()
record = False
@app.route("/gamepad_data", methods=['POST'])
def gamepad_data():
	data = request.get_json()
	bottons = data['bottons']
	axis = data['axes']
	bot_move = axis[:2]
	bot_move[1] = - bot_move[1]
	camera_move = axis[2:]
	b,a,y,x = bottons[:4]
	u = bot_move[0]+bot_move[1]
	v = -bot_move[0]+bot_move[1]
	u /= 2**0.5
	v /= 2**0.5
	print(axis)
	if abs(u) < 0.05 : u = 0
	if abs(v) < 0.05 : v = 0
	if abs(axis[2]) < 0.05 : axis[2] = 0
	if abs(axis[3]) < 0.05 : axis[3] = 0
	bot.axis = [u,v,axis[2],-axis[3]]
	bot.event.set()
	global last
	msg = ""
	if a and time.time()-last > 1:
		last = time.time()
		Camera().shoot()
		msg = "Shoot"
	global record
	if x and not record:
		msg = "Start Record"
		record = True
		Camera().start_record()
	elif y and record:
		msg = "End Record"
		Camera().end_record()
		record = False
	return Response(msg)

@app.route('/gamepad_test')
def gamepad_test():
	return render_template('gamepad.html')

@app.route('/shoot')
def shoot():
	global last
	if time.time()-last > 1:
		last = time.time()
		Camera().shoot()
		return "Complete"
	else :
		return "too fast"

@app.route('/start')
def start():
	Camera().start_record()
	return "Complete"
@app.route('/end')
def end():
	Camera().end_record()
	return "finish"
if __name__ == '__main__':
	app.run(host='0.0.0.0', threaded=True)
