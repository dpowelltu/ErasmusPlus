import network
from machine import Pin
import time
import ujson
from umqtt.simple import MQTTClient



#wifi

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")



# ==== MQTT SETUP ====
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "pub/cleaning/status"
client = MQTTClient("esp32_cleaner", MQTT_BROKER)
client.connect()

# ==== HARDWARE ====
button = Pin(14, Pin.IN, Pin.PULL_UP)  # start cleaning
led = Pin(2, Pin.OUT)                  # status indicator

# ==== STATES ====
IDLE = 0
DIRTY = 1
CLEANING = 2
CLEANED = 3

state = IDLE

# ==== TIMING ====
last_clean_time = time.time()
cleaning_duration = 10          # seconds (simulate cleaning)
dirty_threshold = 30            # seconds before needs cleaning

cleaning_start = 0

# ==== REPORT FUNCTION ====
def report():
    elapsed = time.time() - last_clean_time
    
    message = ujson.dumps({
        "state": state,
        "time_since_clean": int(elapsed)
    })
    
    client.publish(MQTT_TOPIC, message)
    print(message)

last_report = 0

# ==== MAIN LOOP ====
while True:
    now = time.time()
    
    # --- STATE MACHINE ---
    
    if state == IDLE:
        led.value(0)
        
        if now - last_clean_time > dirty_threshold:
            state = DIRTY
            print("System Dirty")
    
    elif state == DIRTY:
        led.value(1)  # alert
        
        if button.value() == 0:  # pressed
            state = CLEANING
            cleaning_start = now
            print("System Clean Started")
    
    elif state == CLEANING:
        led.value(not led.value())
        time.sleep(0.2)
        
        if now - cleaning_start > cleaning_duration:
            state = CLEANED
            last_clean_time = now
            print("System Clean Complted")            
    
    elif state == CLEANED:
        led.value(0)
        report()   # send update once cleaning finishes
        time.sleep(2)
        state = IDLE
        print("System Going To idle")
    
# --- PERIODIC REPORT ---


    if now - last_report > 10:
        report()
        last_report = now
    
    time.sleep(0.1)