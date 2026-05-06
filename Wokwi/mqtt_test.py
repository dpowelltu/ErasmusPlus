"""
MicroPython TUD IoT Smart Pub!

"""

import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient


# MQTT Server Parameters
MQTT_CLIENT_ID = "tudublin-smartpub-demo"
MQTT_BROKER    = "broker.hivemq.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "dp_test"




print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")



prev_weather = ""
while True:
  print("MQTT Test... ", end="")
  client.publish(MQTT_TOPIC, "Test")



  time.sleep(5)