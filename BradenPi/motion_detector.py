import time
import sys
import cv2
import paho.mqtt.client as mqtt
import http.client
import urllib

# Motion threshold: tune for sensitivity to motion
MOTION_THRESHOLD = 10000000
PORT = 8883
BuzzerPin = 4
CERTS = '/etc/ssl/certs/ca-certificates.crt'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# these constants must be set for broker authentication
USERNAME = 'cs326'   
PASSWORD = 'piot' 

# these constants must be set for notification authentication (via api.pushover.net)
user_key = 'ut9ytxbombk8as7ze2k8p1nhpt1b6m'
api_key = 'anq7jacdsi6wivyizb1uvs2mnxwt4v' 

#given a string, this method sends that string to your phone in the form of a notification 
#(presuming you have already connected the app and have correct constants for user_key and api_key)
def send_notification(text):
    connect = http.client.HTTPSConnection("api.pushover.net:443")
    post_data = {'user': user_key, 'token': api_key, 'message': text}
    connect.request("POST", "/1/messages.json",
                     urllib.parse.urlencode(post_data), {"Content-type": "application/x-www-form-urlencoded"})

#sends "filename.avi" as a byte array to topic btl7/motion
def send_file():
    f=open("filename.avi", "rb")
    fileContent = f.read()
    byteArr = bytearray(fileContent)
    print(len(byteArr))
    time.sleep(3)
    client.publish('btl7/motion', byteArr)

#Return grayscale image from camera if capture successful
def get_frame(cap):
    ret, frame = cap.read()
    if not ret:
        print('Frame capture failed...')
        sys.exit(1)    
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#prints to terminal whenever MQTT publishes
def on_publish(client, userdata, mid):
    print("MQTT data published")

#prints to terminal whenever MQTT connects
def on_connect(client, userdata, flags, rc):
    if rc==0:
        print('Connected to {BROKER}')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')
        sys.exit(1)
    

# Initialize camera
print("Initializing camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('Cannot open camera...')
    sys.exit(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 2)

#initialize video 'saver'
size = (640, 480)
result = cv2.VideoWriter('filename.avi', 
                         cv2.VideoWriter_fourcc(*'MJPG'),
                         4, size)

#initialize MQTT
# Setup MQTT client and callbacks
client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD) # remove for anonymous access
client.on_connect = on_connect
client.tls_set(CERTS)
client.on_publish = on_publish

# Connect to MQTT broker and subscribe to the button topic
client.connect(BROKER, PORT, 60)


# initialize last frame
last_frame = get_frame(cap)

# Continuously capture frames from the camera
try:
    while True:
        # grab a frame
        current_frame = get_frame(cap)

        # compute the abs of difference between current and last frame
        frameDelta = cv2.absdiff(current_frame, last_frame)
        diff = frameDelta.sum()

        # If diff > threshold, report motion detected
        if diff > MOTION_THRESHOLD:
            print('motion detected!')

            #notify owner that motion has been sensed
            send_notification("INTRUDER")

            #will takes 50 frames and appends them to filename.avi whenever motion is sensed
            for x in range(50):
                ret, frame = cap.read()
        
                if ret == True: 
            
                    # Write each frame into the file 'filename.avi'
                    result.write(frame)
            print('done taking video')
            time.sleep(3)

            #sends the file multiple times to ensure that it gets sent (we had an issue where
            # the file is only actually sent a fraction of the time)
            send_file()
            send_file()
            send_file()
            send_file()
            send_file()
            time.sleep(2)
            last_frame = get_frame(cap)
        else:
            last_frame = current_frame

except KeyboardInterrupt:
    print('Done')
    cap.release()
