import paho.mqtt.client as mqtt
import sys

# Constants
PORT = 8883
QOS = 0
CERTS = '/etc/ssl/certs/ca-certificates.crt'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# Note: these constants must be set for broker authentication
USERNAME = 'cs326'   # broker authentication username
PASSWORD = 'piot'   # broker authentication password

#prints to terminal whenever MQTT publishes
def on_publish(client, userdata, mid):
    ''' Callback when connecting to the MQTT broker
    '''
    print("Message published")
        
#prints to terminal whenever MQTT connects
def on_connect(client, userdata, flags, rc):
    ''' Callback when connecting to the MQTT broker
    '''
    if rc==0:
        print(f'Connected to {BROKER}')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')
        sys.exit(1)

#whenever there
def on_message(client, data, msg):
    if msg.topic == 'oko/buzzer':
        print(f'Received message {msg.payload}')

client = mqtt.Client()
client.username_pw_set(USERNAME,password=PASSWORD)
client.on_connect=on_connect
client.on_message=on_message
client.on_publish=on_publish
client.tls_set(CERTS)
client.connect(BROKER, PORT, 60)
client.publish('oko/buzzer', "engage")

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    print('Done')