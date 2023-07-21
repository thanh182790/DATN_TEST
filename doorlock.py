import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
from pad4pi import rpi_gpio
import sys
sys.path.insert(0, '/home/pi/Desktop/Test/lcd/drivers')
import I2C_LCD_driver
from threading import Thread


from imutils.video import VideoStream
import face_recognition
import numpy as np
import imutils
import pickle
import cv2
import os
import pigpio

import pyrebase

import  pyshine as ps #  pip3 install pyshine==0.0.9
#initial for database
config = {     
  "apiKey": "AIzaSyAOMX9Qrb-y6DHZG22JqBJNTCh-3AGY2Ug",
  "authDomain": "project-smart-lock.firebaseapp.com",
  "databaseURL": "https://project-smart-lock-default-rtdb.firebaseio.com",
  "storageBucket": "project-smart-lock.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

# variable to save Id user in RTDB that has face or ID card correctly
global IdUser
IdUser = ""
# when start must be set open in firebase = false to prevent door open when start 
db.child("Global_variable").child("open").set("False")

#initial for face recogition
PROTOTXT_DETECTOR = "/home/pi/Desktop/Face_reconition/deploy.prototxt"
MODLE_DETECTOR = "/home/pi/Desktop/Face_reconition/res10_300x300_ssd_iter_140000.caffemodel"
PATH_ENCODING = "/home/pi/Desktop/Face_reconition/encoding.pickle"
CONFIDENCE = 0.99
THRESOLD_MATCH_FACE_ENCODING = 0.4
detector_net = cv2.dnn.readNetFromCaffe(PROTOTXT_DETECTOR, MODLE_DETECTOR)
kwargs_picamera= {"brightness": 70,"contrast": 20, "awb_mode":"tungsten"}

with open(PATH_ENCODING, 'rb') as file:
		encoded_data = pickle.loads(file.read())

print('[INFO] starting video stream...')
vs = VideoStream(usePiCamera = True,resolution=(1280, 720),framerate=30,**kwargs_picamera).start()
# vs =  VideoStream(src=1).start()
time.sleep(2) 

#variable global
DEFAULT_LEN_PASS = 4
DEFAULT_PASSWORD = "1234"
DEFAULT_RFID = ["630038141450", "691502327622"]


INPUT_PASS = ""
DOOR_CLOSED = True
OPEN_BY_APP = False
CLOSE_BY_APP = False
DELAY_UNLOCK = False

KEYPAD = [
	[1, 2, 3, "A"],
	[4, 5, 6, "B"],
	[7, 8, 9, "C"],
	["*", 0, "#", "D"]
]

ROW_PINS = [26, 19, 13, 6] # Borad numbering
COL_PINS = [21, 20, 16, 5] # Board numbering

LED_OK = 0
LED_NOT_OK = 1
SER_VO = 18
SENSOR_PIN = 12

#setup PIN
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LED_OK, GPIO.OUT)
GPIO.setup(LED_NOT_OK, GPIO.OUT)
GPIO.setup(SENSOR_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP)


GPIO.output(LED_OK, GPIO.LOW)
GPIO.output(LED_NOT_OK, GPIO.LOW)

#initial servo
# connect servo to the RPI
pi = pigpio.pi()
pi.set_servo_pulsewidth(SER_VO, 0)
if GPIO.input(SENSOR_PIN):
	pi.set_servo_pulsewidth(SER_VO, 1000) #If when start door open -> close door

#initial Lcd
My_lcd = I2C_LCD_driver.Lcd() 
My_lcd.lcd_clear()
My_lcd.lcd_display_string("WELLCOM SYSTEM",0,1)



# Create a object for the RFID module
read = SimpleMFRC522()

#thread to check if door open the will close after 5s, it will be blocked when CLOSE_BY_APP = True or DELAY_UNLOCK = True
def SensorHandlerThread():
	global DOOR_CLOSED, OPEN_BY_APP
	while True:
		while CLOSE_BY_APP != True and DELAY_UNLOCK != True:
			if GPIO.input(SENSOR_PIN): #if door is openning 
				time.sleep(5)
				pi.set_servo_pulsewidth(SER_VO, 1000) # close door
				GPIO.output(LED_OK, GPIO.LOW)
				My_lcd.lcd_clear()
				My_lcd.lcd_display_string("DOOR CLOED",1,3)
				time.sleep(0.3)
				My_lcd.lcd_clear()
				DOOR_CLOSED = True
				print(f"DOOR_CLOSED = {DOOR_CLOSED}")
				#if has signal open from APP -> re set value OPEN_BY_APP
				if OPEN_BY_APP:
					OPEN_BY_APP = False 

def OpenFromAppThread():
	while True:
		opendoor = db.child("Global_variable").child("open").get()
		if(opendoor.val() == "True"):
			db.child("Global_variable").child("open").set("False")
			if GPIO.input(SENSOR_PIN) == GPIO.LOW: #if door is closing
				GPIO.output(LED_OK,GPIO.HIGH)
				pi.set_servo_pulsewidth(SER_VO, 2000) #open door
				global OPEN_BY_APP, DOOR_CLOSED
				DOOR_CLOSED = False
				OPEN_BY_APP = True


def CloseFromAppThread():
	while True:
		closedoor = db.child("Global_variable").child("close").get()
		if(closedoor.val() == "True"):
			db.child("Global_variable").child("close").set("False")
			if GPIO.input(SENSOR_PIN) == GPIO.HIGH:#if door is openning
				global CLOSE_BY_APP, DOOR_CLOSED
				CLOSE_BY_APP = True
				pi.set_servo_pulsewidth(SER_VO, 1000) #close door
				DOOR_CLOSED = False
				GPIO.output(LED_OK,GPIO.LOW)
				CLOSE_BY_APP = False

def DelayUnlockThread():
	while True:
		# Pull value from firebase
		allowDelayUnlock = db.child("Global_variable").child("delayUnlock").child("allowDelay").get()
		# If the mobile app user has triggered a delayed unlock:
		if (allowDelayUnlock.val() == 'True'):
			global DELAY_UNLOCK, DOOR_CLOSED
			# Notify facial_recognition_thread to unlock to any face
			DELAY_UNLOCK = True
			# Reset Firebase variable
			db.child("Global_variable").child("delayUnlock").child("allowDelay").set("False")
			# Get time delay value
			timeDelay = db.child("Global_variable").child("delayUnlock").child("timeDelay").get()
			timeDelay = int(timeDelay.val())
			timeRemaining = timeDelay
			if GPIO.input(SENSOR_PIN) == GPIO.LOW: #if door is closing
				GPIO.output(LED_OK,GPIO.HIGH)
				pi.set_servo_pulsewidth(SER_VO, 2000) #open door
				DOOR_CLOSED = False
				My_lcd.lcd_clear()
				My_lcd.lcd_display_string("DOOR FREE", 1 , 2)
				My_lcd.lcd_display_string("Remain:", 2 , 1)
				My_lcd.lcd_display_string("mins", 2 , 13)
			My_lcd.lcd_display_string("   ", 2, 9)
			for i in range(timeDelay+1):
				My_lcd.lcd_display_string(str(timeRemaining), 2, 9)
				db.child("Global_variable").child("delayUnlock").child("timeRemain").set(timeRemaining)
				print('Time Remaining: %s minute(s)'%timeRemaining)
				if(timeRemaining == 0):
					My_lcd.lcd_clear()
					My_lcd.lcd_display_string("TIME OUT FREE",1,1)
					My_lcd.lcd_display_string("DOOR CLOSED",2,2)
					pi.set_servo_pulsewidth(SER_VO, 1000) #close door
					GPIO.output(LED_OK,GPIO.LOW)
					print("breaking")
					break
				timeRemaining = timeRemaining - 1
				# Update time remaining every minute
				for i in range(60):
					# Check if the delay has been cancelled by the user
					cancelDelay = db.child("Global_variable").child("delayUnlock").child("cancelDelay").get()
					if(cancelDelay.val() == "True"):
						db.child("Global_variable").child("delayUnlock").child("cancelDelay").set("False")
						timeRemaining = 0
						db.child("Global_variable").child("delayUnlock").child("timeRemain").set(timeRemaining)
						break
					time.sleep(1)
			DELAY_UNLOCK = False
			DOOR_CLOSED = True
		time.sleep(2)
			
def KeypadHandlerInterrupt(key):
	print(f"Received key from interrupt:: {key}")
	global INPUT_PASS,  DOOR_CLOSED
	if DOOR_CLOSED:
		if "A" == key:
			DEFAULT_PASSWORD = db.child("Global_variable").child("passdoor").get()
			if(INPUT_PASS == DEFAULT_PASSWORD.val()):
				DOOR_CLOSED = False
				pi.set_servo_pulsewidth(SER_VO, 2000) # position anti-clockwise
				GPIO.output(LED_OK, GPIO.HIGH)
				print(f"DOOR_CLOSED = {DOOR_CLOSED}")
				My_lcd.lcd_clear()
				My_lcd.lcd_display_string(" PASS CORRECT",1,2)
				My_lcd.lcd_display_string("DOOR OPENED",2,3)
			else:
				GPIO.output(LED_NOT_OK, GPIO.HIGH)
				My_lcd.lcd_clear()
				time.sleep(0.1)
				My_lcd.lcd_display_string("PASS INCORRECT!",1,1)
				time.sleep(0.1)
				GPIO.output(LED_NOT_OK, GPIO.LOW)
				time.sleep(0.1)
				GPIO.output(LED_NOT_OK, GPIO.HIGH)	
				time.sleep(0.1)
				GPIO.output(LED_NOT_OK, GPIO.LOW)
				print(f"DOOR_CLOSED = {DOOR_CLOSED}")
			INPUT_PASS =""
			print(f"INPUT PASS =  {INPUT_PASS}")
		elif "C" == key:
			INPUT_PASS = ""
			My_lcd.lcd_clear()
			My_lcd.lcd_display_string("ENTER PASSWORD",1,1)
		else:
			if len(INPUT_PASS) < DEFAULT_LEN_PASS:
				INPUT_PASS += str(key)
				My_lcd.lcd_clear()
				My_lcd.lcd_display_string("ENTER PASSWORD",1,1)
				My_lcd.lcd_display_string(INPUT_PASS,2,3)
				print(INPUT_PASS)
def KeypadHandlerThread():
		factory = rpi_gpio.KeypadFactory()
		keypad = factory.create_keypad(keypad=KEYPAD,row_pins=ROW_PINS, col_pins=COL_PINS) # makes assumptions about keypad layout and GPIO pin numbers
		
		keypad.registerKeyPressHandler(KeypadHandlerInterrupt)

		print("Press buttons on your keypad. Ctrl+C to exit.")
		while True:
			time.sleep(1)

#Return a Dicitonary example: {'Iduser1':[RFID_value_1,Lable_name1,Id_user_sign_in_1(optional)],
# 'Iduser2':[RFID_value_2,Lable_name_2,Id_user_sign_in_2(optional)]}
def GetDictValueAuthenUser():
	RefUsers = db.child("users").get()
	DictValAuthUser = {}
	for user in RefUsers.each():
		 DictValAuthUser[user.val()['id']] = [user.val()['idcard'],user.val()['lablename']]
	return DictValAuthUser

def CheckIdExistinRTDB(id,lstValAuth, lsIdUser):
	global IdUser
	for x in lstValAuth:
		if id in x:
			IdUser = lsIdUser[lstValAuth.index(x)]
			return True
	return False
def RFIDThread():
	global DOOR_CLOSED, INPUT_PASS
	print(DOOR_CLOSED)
	while True:
		id,Tag = read.read()
		id = str(id)
		print(id)
		addRFID = db.child("Global_variable").child("rfid").child("addrfid").get()
		deleteRFID = db.child("Global_variable").child("rfid").child("deleterfid").get()
		if(addRFID.val() == 'True'):
			db.child("Global_variable").child("rfid").child("addrfid").set("False")
			My_lcd.lcd_clear()
			My_lcd.lcd_display_string("Place your RFID",1,0)
			if(id == ""):
				db.child("Global_variable").child("rfid").child("value").set("xxx")
			else:
				db.child("Global_variable").child("rfid").child("value").set(id)
			My_lcd.lcd_clear()
			My_lcd.lcd_display_string("New Id Card:",1,1)
			if(id == ""):
				My_lcd.lcd_display_string("Error",1,11)
			else:
				My_lcd.lcd_display_string(id,2,2)
			time.sleep(2)
			My_lcd.lcd_clear()
		elif (deleteRFID.val() == 'True'):
			pass
		else:
			if DOOR_CLOSED:
				dictValAuth = GetDictValueAuthenUser()
				listValAuth = list(dictValAuth.values())
				listIDUser = list(dictValAuth.keys())
				if (id != "") and CheckIdExistinRTDB(id, listValAuth, listIDUser):
					#Need get Id of user tag and time open door to put RTDB
					print(f"Currenr Id = {IdUser}")
					DOOR_CLOSED = False
					pi.set_servo_pulsewidth(SER_VO, 2000) # open door
					GPIO.output(LED_OK, GPIO.HIGH)
					print(f"DOOR_CLOSED = {DOOR_CLOSED}")
					My_lcd.lcd_clear()
					My_lcd.lcd_display_string(" TAG CORRECT",1,2)
					My_lcd.lcd_display_string("DOOR OPENED",2,3)
					
				else:
					GPIO.output(LED_NOT_OK, GPIO.HIGH)
					time.sleep(0.1)
					GPIO.output(LED_NOT_OK, GPIO.LOW)
					time.sleep(0.1)
					GPIO.output(LED_NOT_OK, GPIO.HIGH)
					time.sleep(0.1)
					GPIO.output(LED_NOT_OK, GPIO.LOW)
					My_lcd.lcd_clear()
					My_lcd.lcd_display_string("TAG INCORRECT!",1,1)
				INPUT_PASS =""
		

# def AddFaceThread():
	

def FaceHandlerThread():
	global INPUT_PASS, DOOR_CLOSED
	OK = 1
	# initialize the video stream and allow camera to warmup
	# print('[INFO] starting video stream...')
	# # vs = VideoStream(usePiCamera = True,resolution=(1280, 720),framerate=30,**kwargs_picamera).start()
	# vs =  VideoStream(src=1).start()
	# time.sleep(2) # wait camera to warmup
	while True:
		frame = vs.read()
		frame = imutils.resize(frame, width=400)
		(h, w) = frame.shape[:2]
		blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
		# pass the blob through the network 
		# and obtain the detections and predictions
		detector_net.setInput(blob)
		detections = detector_net.forward()
		
		if DOOR_CLOSED:
			# iterate over the detections
			for i in range(0, detections.shape[2]):
				# print(detections.shape[2])
				# extract the confidence (i.e. probability) associated with the prediction
				confidence = detections[0, 0, i, 2]

				# filter out weak detections
				if confidence > CONFIDENCE:
					# compute the (x,y) coordinates of the bounding box
					# for the face and extract the face ROI
					box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
					(startX, startY, endX, endY) = box.astype('int')
					
					# expand the bounding box a bit
					# (from experiment, the model works better this way)
					# and ensure that the bounding box does not fall outside of the frame
					startX = max(0, startX)
					startY = max(0, startY)
					endX = min(w, endX)
					endY = min(h, endY)
					bounding_box = [(startY, endX, endY, startX)] # have to rearrange the coordinates to match bounding box of function face_encodings
					
					#Should use frame be read from "vs.read()" to encoding instead of image after select ROI "frame[startY:endY, startX:endX]" because in some case can not encoding
					# compute the face embedding
					# face recognition
					face_to_recog_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
					encodings = face_recognition.face_encodings(face_to_recog_rgb, bounding_box)
					# initialize the default name if it doesn't found a face for detected faces
					name = "X"
					if len(encodings) != 0:
						for encoding in encodings:
							matches = face_recognition.compare_faces(encoded_data['encodings'], encoding,THRESOLD_MATCH_FACE_ENCODING)
							# print(matches)
							print("\n")
							if True in matches:
								# find the indexes of all matched faces then initialize a dict
								# to count the total number of times each face was matched
								matchedIdxs = [i for i, b in enumerate(matches) if b]
								counts = {}
								
								# loop over matched indexes and count
								for i in matchedIdxs:
									name = encoded_data['names'][i]
									counts[name] = counts.get(name, 0) + 1
									
								# get the name with the most count
								name = max(counts, key=counts.get)
								if name != "X":
									DOOR_CLOSED = False
									pi.set_servo_pulsewidth(SER_VO, 2000) # open door
									GPIO.output(LED_OK, GPIO.HIGH)
									print("welcom " + name + " back home")
									My_lcd.lcd_clear()
									My_lcd.lcd_display_string("welcom " + name,1,2)
								elif name == "X":
									print('Face match found!')
									My_lcd.lcd_clear()
									My_lcd.lcd_display_string("Face match found!",1,1)
									GPIO.output(LED_NOT_OK, GPIO.HIGH)
									time.sleep(0.1)
									GPIO.output(LED_NOT_OK, GPIO.LOW)
									time.sleep(0.1)
									GPIO.output(LED_NOT_OK, GPIO.HIGH)
									time.sleep(0.1)
									GPIO.output(LED_NOT_OK, GPIO.LOW)
								INPUT_PASS = ""	
						cv2.putText(frame, name, (startX, startY - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,130,255),2 )
						cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 4)
					else :
						cv2.putText(frame, "Can't not encoding face", (startX, startY - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0,130,255),2 )
						cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 0, 255), 4)

		# OK = not OK
		# frame = cv2.resize(frame, (780, 540),interpolation = cv2.INTER_LINEAR)
		cv2.imshow('Frame', frame)
		key = cv2.waitKey(1) & 0xFF
		
		# if 'q' is pressed, stop the loop
		# if that person appears 10 frames in a row, stop the loop
		# you can change this if your GPU run faster
		if key == ord('q'):
			break
	vs.stop()
	cv2.destroyAllWindows()

def StreamThread():
	HTML="""
	<html>
	<head>
	<meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Live Streaming From WebCam</title>
	</head>

	<body>
	<center><h1 style='color:green' >CCTV Camera </h1></center>
	<center><img src="stream.mjpg" width='100%' height='auto' autoplay playsinline></center>
	</body>
	</html>
	"""

	StreamProps = ps.StreamProps
	StreamProps.set_Page(StreamProps,HTML)
	address = ('192.168.1.69',9000) # Enter your IP address 
	try:
		StreamProps.set_Mode(StreamProps,'cv2')
		capture = cv2.VideoCapture(1, cv2.CAP_V4L)
		capture.set(cv2.CAP_PROP_BUFFERSIZE,4)
		capture.set(cv2.CAP_PROP_FRAME_WIDTH,320)
		capture.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
		capture.set(cv2.CAP_PROP_FPS,30)
		StreamProps.set_Capture(StreamProps,capture)
		StreamProps.set_Quality(StreamProps,90)
		server = ps.Streamer(address,StreamProps)
		print('Server started at','http://'+address[0]+':'+str(address[1]))
		server.serve_forever()
		
	except KeyboardInterrupt:
		capture.release()
		server.socket.close()

try:
	T1 = Thread(target = SensorHandlerThread)
	T2 = Thread(target = KeypadHandlerThread)
	T3 = Thread(target = RFIDThread)
	T4 = Thread(target = FaceHandlerThread)
	T5 = Thread(target = OpenFromAppThread)
	T6 = Thread(target = CloseFromAppThread)
	T7 = Thread(target = StreamThread)
	T8 = Thread(target = DelayUnlockThread)

	T1.start()
	T2.start()
	T3.start()
	T4.start()
	T5.start()
	T6.start()
	T7.start()
	T8.start()

	T1.join()
	T2.join()
	T3.join()
	T4.join()
	T5.join()
	T6.join()
	T7.join()
	T8.join()

except KeyboardInterrupt:
	print("ngo oi")
	My_lcd.lcd_clear()
	print("System down")
	# T1.join()

