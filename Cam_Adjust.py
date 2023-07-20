from imutils.video import VideoStream
from itertools import cycle
from pprint import pprint
import time
import cv2

global g_viStream
kwargs_picamera= {"brightness": 70,"contrast": 50}
# Init VideoStream
g_viStream = VideoStream(usePiCamera=True, **kwargs_picamera).start()
time.sleep(2.0)

# Gia tri mac dinh cho auto white balance ISO mode
awbModes = ["off", "auto", "sunlight", "cloudy", "shade",
	"tungsten", "fluorescent", "flash", "horizon"]
isoModes = [0, 100, 200, 320, 400, 500, 640, 800, 1600]


# init 2 cycles pools
isoModesPool = cycle(isoModes)
awbModesPool = cycle(awbModes)

#Dictionary chua nhung thuoc tinh cua camera co the thay doi
g_picamSettings = {
	"awb_mode": None,
	"awb_gains": None,
	"brightness": None,
	"color_effects": None,
	"contrast": None,
	"drc_strength": None,
	"exposure_compensation": None,
	"exposure_mode": None,
	"flash_mode": None,
	"hflip": None,
	"image_denoise": None,
	"image_effect": None,
	"image_effect_params": None,
	"iso": None,
	"meter_mode": None,
	"rotation": None,
	"saturation": None,
	"sensor_mode": None,
	"sharpness": None,
	"shutter_speed": None,
	"vflip": None,
	"video_denoise": None,
	"video_stabilization": None,
	"zoom": None
}

def getPicamSettings(output=False):
    global g_picamSettings
    global g_viStream

    #local var de giu setting hien tai
    curPicamSettings = {}

    #print status message neu enable output
    if output:
        print("[INFO] Read Pi cam settings...")
    
    #Get thuoc tinh cua tung key trong g_viStream object
    for attr in g_picamSettings.keys():
        curPicamSettings[attr] = getattr(g_viStream.camera, attr)
    
    # print setting neu enable output
    if output:
        pprint(curPicamSettings)

    g_picamSettings = curPicamSettings

    return curPicamSettings

def getSinglePicamSettings(setting):
    curPicamSettings = getPicamSettings()
    return curPicamSettings[setting]

#function de kich hoat new setting
def activatePicamSettings(**args):
    global g_viStream
    g_viStream.stop()
    time.sleep(0.25)
    g_viStream = VideoStream(usePiCamera=True, **args).start()
    print(args)
    time.sleep(2)
    print("[INFO] suceed! ")

def setPicamSettings(**args):
    global g_picamSettings
    global g_viStream

    # Luu tru setting hien tai
    print("[INFO] read settings...")
    curPicamSettings = getPicamSettings()

    # print va update gia tri setting moi
    for (attr,value) in args.items():
        print("[INFO] Old setting {}->New setting {}".format(curPicamSettings[attr],value))
        curPicamSettings[attr] = value

    # khoi tao bien de giu cac thuoc tinh bi trung trong curPicamSettings va xoa no
    attrsToDel = []
    for attr in curPicamSettings.keys():
        if curPicamSettings[attr] == None:
            attrsToDel.append(attr)
    pprint(attrsToDel)
    for attr in attrsToDel:
        curPicamSettings.pop(attr)

    args = curPicamSettings
    activatePicamSettings(**args)
# Loop va doc frame anh tu camera

print("Current setting ")
print(getPicamSettings(True))
while True:
    # doc 1 frame
    frame = g_viStream.read()

    #xuat frame ra man hinh
    cv2.imshow("Frame",frame)
    key = cv2.waitKey(1)

    #Xu ly su kien nut nhan
    if key == ord("q"):
        break
    elif key == ord("w"): # auto white balance
        awbMode = getSinglePicamSettings("awb_mode")
        setPicamSettings(awb_mode=next(awbModesPool))
    elif key == ord("i"): # ISO
        isoMode = getSinglePicamSettings("iso")
        setPicamSettings(iso=next(isoModesPool))
    elif key == ord("b"): # brightness
        brightness = getSinglePicamSettings("brightness")
        setPicamSettings(brightness=brightness+5)
    elif key == ord("d"): # darken brightness
        brightness = getSinglePicamSettings("brightness")
        setPicamSettings(brightness=brightness-1)
    elif key == ord("c"): # darken brightness
        contrast = getSinglePicamSettings("contrast")
        setPicamSettings(contrast=contrast+5)
    elif key == ord("r"): # read setting
        settings = getPicamSettings(output=True)

g_viStream.stop()
cv2.destroyAllWindows()