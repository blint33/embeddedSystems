import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import sys

# Constants
PORT = 1883
QOS = 0
CERTS = '/etc/ssl/certs/ca-certificates.crt'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# Note: these constants must be set for broker authentication
USERNAME = ''   # broker authentication username
PASSWORD = ''   # broker authentication password
BuzzerPin = 4
#GPIO initialization
GPIO.setmode(GPIO.BCM)
GPIO.setup(BuzzerPin, GPIO.OUT)
buzzer = GPIO.PWM(BuzzerPin, 1600)

#prints out a message when broker is connected 
def on_connect(client, userdata, flags, rc):
    ''' Callback when connecting to the MQTT broker
    '''
    if rc==0:
        print(f'Connected to {BROKER}')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')
        sys.exit(1)

#whenever a message is recieved from topic oko/buzzer, this sets PWM of BuzzerPin 
# to 10 for 10 seconds (which should turn the buzzer on for ten seconds if it's hooked up right)
def on_message(client, data, msg):
    if msg.topic == 'oko/buzzer':
        buzzer.start(10)
        time.sleep(10)
        buzzer.start(0)

#initializes broker
client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD)
client.on_connect=on_connect
client.on_message=on_message
client.connect(BROKER, PORT, 60)
client.subscribe('oko/buzzer', qos=QOS)

#infinite loop of waiting for a message from broker, until keyboard interrupts
try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print('Done')
