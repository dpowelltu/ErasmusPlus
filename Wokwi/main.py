"""
MicroPython TUD IoT Smart Pub!

"""

import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

pulse_count = 0

# MQTT Server Parameters
MQTT_CLIENT_ID = "tudublin-smartpub-demo"
MQTT_BROKER    = "broker.hivemq.com"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "dpweather"

sensor = dht.DHT22(Pin(15))
button = Pin(12, Pin.IN, Pin.PULL_UP)
last_button = button.value()
led = Pin(23, Pin.OUT)


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

def pulse_callback(pin):
    global pulse_count
    pulse_count += 1

# Trigger on falling edge (typical for pull-up wiring)
button.irq(trigger=Pin.IRQ_FALLING, handler=pulse_callback)
last_temp=0.0
last_pulse_count=0
prev_weather = ""
while True:
  print("Measuring weather conditions... ", end="")
  sensor.measure() 
  message = ujson.dumps({
    "temp": sensor.temperature(),
    "humidity": sensor.humidity(),
  })


  #if message != prev_weather:
  if(abs(sensor.temperature()-last_temp)>1):
    print("Updated!")
    print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
    client.publish(MQTT_TOPIC, message)
    prev_weather = message
    last_temp = sensor.temperature();
  else:
    print("No change")

  led.value(0)
  if pulse_count != last_pulse_count:
    last_pulse_count = pulse_count
    pls_message = ujson.dumps({"flow": pulse_count })
    client.publish("dppulse", pls_message)
    led.value(1)

  if button.value() != last_button:  # pressed
    print("Button changed")
    last_button = button.value()
    btn_message = ujson.dumps({"button": button.value() })
    client.publish("dpbutton", btn_message)
 
  print("pulse count = ", pulse_count)


  time.sleep(1)
