import paho.mqtt.client as mqtt
import sys

# Constants
PORT = 1883
QOS = 0
CERTS = '/etc/ssl/certs/ca-certificates.crt'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# Note: these constants must be set for broker authentication
USERNAME = 'cs326'   # broker authentication username
PASSWORD = 'piot'   # broker authentication password

#prints to terminal whenever MQTT connects
def on_connect(client, userdata, flags, rc):
    ''' Callback when connecting to the MQTT broker
    '''
    if rc==0:
        print(f'Connected to {BROKER}')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')
        sys.exit(1)

#whenever there is a message sent, and its topic is btl7/motion, the message is saved to 
#intruderVid.avi
def on_message(client, data, msg):
    if msg.topic == 'btl7/motion':
        print(f'Received message {msg.payload}')
        print(msg.payload)
        with open("intruderVid.avi", "wb") as f:
            f.write(bytes(msg.payload))

#initializing MQTT
client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD)
client.on_connect=on_connect
client.on_message=on_message
client.connect(BROKER, PORT, 60)
client.subscribe('btl7/motion', qos=QOS)

#continuously loops, listening for a message
try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print('Done')