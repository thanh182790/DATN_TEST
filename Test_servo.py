# import RPi.GPIO as GPIO
# import time

# # setup RPi
# GPIO.setwarnings(False)
# servo_pin = 14
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servo_pin,GPIO.OUT)

# # 50 Hz or 20 ms PWM period
# pwm = GPIO.PWM(servo_pin,50) 

# print("Starting at zero...")
# pwm.start(5) 
# pwm.ChangeDutyCycle(10) 
# time.sleep(4)

# # try:
# #     while True:
# #         print("Setting to zero...")
# #         pwm.ChangeDutyCycle(5) 
# #         time.sleep(4) 
# #         print("Setting to 90...")
# #         pwm.ChangeDutyCycle(10) # door open 
# #         time.sleep(4)

# # except KeyboardInterrupt:
# #     pwm.stop() 
# #     GPIO.cleanup()
# #     print("Program stopped")

# import io
# import picamera
# import logging
# import socketserver
# from threading import Condition
# from http import server


# PAGE="""\
# <html>
# <head>
# <title>Raspberry Pi - Surveillance Camera</title>
# </head>
# <body>
# <center><h1>Raspberry Pi - Surveillance Camera</h1></center>
# <center><img src="stream.mjpg" width="640" height="480"></center>
# </body>
# </html>
# """

# class StreamingOutput(object):
# 	def __init__(self):
# 		self.frame = None
# 		self.buffer = io.BytesIO()
# 		self.condition = Condition()

# 	def write(self, buf):
# 		if buf.startswith(b'\xff\xd8'):
# 			# New frame, copy the existing buffer's content and notify all
# 			# clients it's available
# 			self.buffer.truncate()
# 			with self.condition:
# 				self.frame = self.buffer.getvalue()
# 				self.condition.notify_all()
# 			self.buffer.seek(0)
# 		return self.buffer.write(buf)

# class StreamingHandler(server.BaseHTTPRequestHandler):
# 	def do_GET(self):
# 		if self.path == '/':
# 			self.send_response(301)
# 			self.send_header('Location', '/index.html')
# 			self.end_headers()
# 		elif self.path == '/index.html':
# 			content = PAGE.encode('utf-8')
# 			self.send_response(200)
# 			self.send_header('Content-Type', 'text/html')
# 			self.send_header('Content-Length', len(content))
# 			self.end_headers()
# 			self.wfile.write(content)
# 		elif self.path == '/stream.mjpg':
# 			self.send_response(200)
# 			self.send_header('Age', 0)
# 			self.send_header('Cache-Control', 'no-cache, private')
# 			self.send_header('Pragma', 'no-cache')
# 			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
# 			self.end_headers()
# 			try:
# 				while True:
# 					with output.condition:
# 						output.condition.wait()
# 						frame = output.frame
# 					self.wfile.write(b'--FRAME\r\n')
# 					self.send_header('Content-Type', 'image/jpeg')
# 					self.send_header('Content-Length', len(frame))
# 					self.end_headers()
# 					self.wfile.write(frame)
# 					self.wfile.write(b'\r\n')
# 			except Exception as e:
# 				logging.warning(
# 					'Removed streaming client %s: %s',
# 					self.client_address, str(e))
# 		else:
# 			self.send_error(404)
# 			self.end_headers()

# class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
# 	allow_reuse_address = True
# 	daemon_threads = True

# with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
# 	output = StreamingOutput()
# 	#Uncomment the next line to change your Pi's Camera rotation (in degrees)
# 	#camera.rotation = 90
# 	camera.start_recording(output, format='mjpeg')
# 	try:
# 		address = ('', 8000)
# 		server = StreamingServer(address, StreamingHandler)
# 		server.serve_forever()
# 	finally:
# 		camera.stop_recording()


import pigpio
from time import sleep

# connect to the 
pi = pigpio.pi()

# loop forever
while True:


    pi.set_servo_pulsewidth(18, 1000) # position anti-clockwise
    sleep(1)

    pi.set_servo_pulsewidth(18, 2000) # position clockwise
    sleep(1)