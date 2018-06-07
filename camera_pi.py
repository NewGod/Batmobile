import io
import os
import time
import picamera
import threading
try:
	from greenlet import getcurrent as get_ident
except ImportError:
	try:
		from thread import get_ident
	except ImportError:
		from _thread import get_ident


class CameraEvent(object):
	"""An Event-like class that signals all active clients when a new frame is
	available.
	"""
	def __init__(self):
		self.events = {}

	def wait(self):
		"""Invoked from each client's thread to wait for the next frame."""
		ident = get_ident()
		if ident not in self.events:
			# this is a new client
			# add an entry for it in the self.events dict
			# each entry has two elements, a threading.Event() and a timestamp
			self.events[ident] = [threading.Event(), time.time()]
		return self.events[ident][0].wait()

	def set(self):
		"""Invoked by the camera thread when a new frame is available."""
		now = time.time()
		remove = None
		for ident, event in self.events.items():
			if not event[0].isSet():
				# if this client's event is not set, then set it
				# also update the last set timestamp to now
				event[0].set()
				event[1] = now
			else:
				# if the client's event is already set, it means the client
				# did not process a previous frame
				# if the event stays set for more than 5 seconds, then assume
				# the client is gone and remove it
				if now - event[1] > 5:
					remove = ident
		if remove:
			del self.events[remove]

	def clear(self):
		"""Invoked from each client's thread after a frame was processed."""
		self.events[get_ident()][0].clear()


class Camera():
	thread = None  # background thread that reads frames from camera
	frame = None  # current frame is stored here by background thread
	last_access = 0  # time of last client access to the camera
	event = CameraEvent()
	camera = picamera.PiCamera()
	camera.led = False

	def get_frame(self):
		"""Return the current camera frame."""
		Camera.last_access = time.time()

		# wait for a signal from the camera thread
		Camera.event.wait()
		Camera.event.clear()

		return Camera.frame
	@staticmethod
	def frames():
		""""Generator that returns frames from the camera."""
		raise RuntimeError('Must be implemented by subclasses.')
	@classmethod
	def _thread(cls):
		"""Camera background thread."""
		print('Starting camera thread.')
		frames_iterator = cls.frames()
		for frame in frames_iterator:
			Camera.frame = frame
			Camera.event.set()	# send signal to clients
			time.sleep(0)

			# if there hasn't been any clients asking for frames in
			# the last 10 seconds then stop the thread
			if time.time() - Camera.last_access > 10:
				frames_iterator.close()
				print('Stopping camera thread due to inactivity.')
				break
		Camera.thread = None
	def __init__(self):
		"""Start the background camera thread if it isn't running yet."""
		if Camera.thread is None:
			Camera.last_access = time.time()

			# start background frame thread
			Camera.thread = threading.Thread(target=self._thread)
			Camera.thread.start()

			# wait until frames are available
			while self.get_frame() is None:
				time.sleep(0)
	@staticmethod
	def frames():
		time.sleep(2)

		stream = io.BytesIO()
		for _ in Camera.camera.capture_continuous(stream, 'jpeg',
				use_video_port=True, resize = (320,240), ):
			# return current frame
			stream.seek(0)
			yield stream.read()

			# reset stream for next frame
			stream.seek(0)
			stream.truncate()
	@staticmethod
	def shoot():
		mx = 0
		files = os.listdir('image')
		for file in files:
			s = file.split('.')
			if (s[-1]!='jpg') :
				continue
			mx = max(mx,int(s[-2]))
		mx = mx+1
		Camera.camera.capture(os.path.join('image',str(mx)+'.jpg'))
		

	@staticmethod
	def start_record():
		mx = 0
		files = os.listdir('video')
		for file in files:
			s = file.split('.')
			if (s[-1]!='h264') :
				continue
			mx = max(mx,int(s[-2]))
		mx = mx+1
		Camera.camera.start_recording(os.path.join('video',str(mx)+'.h264'))
		Camera.camera.led = True

	@staticmethod
	def end_record():
		Camera.camera.stop_recording()
		Camera.camera.led = False
