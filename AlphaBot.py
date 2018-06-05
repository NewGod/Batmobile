import RPi.GPIO as GPIO
import time
import threading

class AlphaBot(object):

	def __init__(self,in1=12,in2=13,ena=6,in3=20,in4=21,enb=26,s1=27,s2=22):
		self.IN1 = in1
		self.IN2 = in2
		self.IN3 = in3
		self.IN4 = in4
		self.ENA = ena
		self.ENB = enb
		self.S1 = s1
		self.S2	= s2

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.IN1,GPIO.OUT)
		GPIO.setup(self.IN2,GPIO.OUT)
		GPIO.setup(self.IN3,GPIO.OUT)
		GPIO.setup(self.IN4,GPIO.OUT)
		GPIO.setup(self.ENA,GPIO.OUT)
		GPIO.setup(self.ENB,GPIO.OUT)
		GPIO.setup(self.S1,GPIO.OUT)
		GPIO.setup(self.S2,GPIO.OUT)
		self.stop()
		self.PWMA = GPIO.PWM(self.ENA,500)
		self.PWMB = GPIO.PWM(self.ENB,500)
		self.PWMA.start(50)
		self.PWMB.start(50)
		self.PWMC=GPIO.PWM(self.S1,50)
		self.PWMD=GPIO.PWM(self.S2,50)
		self.PWMC.start(0)
		self.PWMD.start(0)
		self.x = -10
		self.y = 0
		self.setServe(0,0)
		self.axis = [0]*4

		self.event = None
		self.thread = threading.Thread(target=self._thread)
		self.thread.start()

		# wait until frames are available
		while self.event is None:
			time.sleep(0)

	def forward(self):
		GPIO.output(self.IN1,GPIO.HIGH)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.HIGH)

	def stop(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.LOW)

	def backward(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.HIGH)
		GPIO.output(self.IN3,GPIO.HIGH)
		GPIO.output(self.IN4,GPIO.LOW)

	def left(self):
		GPIO.output(self.IN1,GPIO.LOW)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.HIGH)

	def right(self):
		GPIO.output(self.IN1,GPIO.HIGH)
		GPIO.output(self.IN2,GPIO.LOW)
		GPIO.output(self.IN3,GPIO.LOW)
		GPIO.output(self.IN4,GPIO.LOW)

	def setPWMA(self,value):
		self.PWMA.ChangeDutyCycle(value)

	def setPWMB(self,value):
		self.PWMB.ChangeDutyCycle(value)

	def setMotor(self, left, right):
		left, right = right, left
		if((right >= 0) and (right <= 100)):
			GPIO.output(self.IN1,GPIO.HIGH)
			GPIO.output(self.IN2,GPIO.LOW)
			self.PWMA.ChangeDutyCycle(right)
		elif((right < 0) and (right >= -100)):
			GPIO.output(self.IN1,GPIO.LOW)
			GPIO.output(self.IN2,GPIO.HIGH)
			self.PWMA.ChangeDutyCycle(- right)
		if((left >= 0) and (left <= 100)):
			GPIO.output(self.IN3,GPIO.LOW)
			GPIO.output(self.IN4,GPIO.HIGH)
			self.PWMB.ChangeDutyCycle(left)
		elif((left < 0) and (left >= -100)):
			GPIO.output(self.IN3,GPIO.HIGH)
			GPIO.output(self.IN4,GPIO.LOW)
			self.PWMB.ChangeDutyCycle(- left)
	
	def setServe(self, dx, dy):
		dx *= 5
		dy *= 5
		self.x += dx
		self.y += dy
		self.x = max(min(self.x,90),-90)
		self.y = max(min(self.y,90),-90)
		self.PWMC.ChangeDutyCycle(7.5-5*self.x/90)
		self.PWMD.ChangeDutyCycle(7.5-5*self.y/90)
		time.sleep(0.02)
		self.PWMC.ChangeDutyCycle(0)
		self.PWMD.ChangeDutyCycle(0)

	def _thread(self):
		print('Start bot thread.')
		self.event = threading.Event()
		while True:
			self.event.wait()
			self.event.clear()
			self.setMotor(self.axis[0]*100, self.axis[1]*100)
			self.setServe(self.axis[2], self.axis[3])
			



