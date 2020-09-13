import network
import utime
from ds3231 import DS3231
from machine import Pin, I2C, PWM
from time import sleep
from ujson import loads
from umqtt.simple import MQTTClient

# MQTT server settings
SERVER = '192.168.1.110'
CLIENT = 'ESP_32_SUNRISE_ALARM'
TOPIC = 'home/alarm'

TIME_FILE = 'time.txt'
WIFI_FILE = 'wifi.txt'

# How long it takes for the LEDs to reach full brightness
SUNRISE_LENGTH = 1800
# For how long the brightness increases mildly
LOW_THRESHOLD = SUNRISE_LENGTH / 2
LOW_THRESHOLD_DUTY = 30
# For how long the light stays on after the alarm
# goes off
KEEP_LIGHT_ON = SUNRISE_LENGTH / 2

MAX_DUTY = 1023
DUTY_DIFF = MAX_DUTY - LOW_THRESHOLD_DUTY

i2c = I2C(sda=Pin(4), scl=Pin(16))
DS = DS3231(i2c)
LEDS = [
    PWM(Pin(17, Pin.OUT), freq=70, duty=0),
    PWM(Pin(18, Pin.OUT), freq=70, duty=0),
    PWM(Pin(19, Pin.OUT), freq=70, duty=0),
    PWM(Pin(21, Pin.OUT), freq=70, duty=0),
    PWM(Pin(22, Pin.OUT), freq=70, duty=0),
    PWM(Pin(33, Pin.OUT), freq=70, duty=0),
    PWM(Pin(25, Pin.OUT), freq=70, duty=0),
    PWM(Pin(26, Pin.OUT), freq=70, duty=0),
]

with open(TIME_FILE, 'r') as infile:
    t = infile.read().splitlines()
    ALARM_HOURS, ALARM_MINUTES, ALARM_SECONDS = int(t[0]), int(t[1]), int(t[2])


def seconds_until_alarm(alarm_hours, alarm_minutes, alarm_seconds):
    """Calculates the number of seconds until alarm goes off"""
    hours = DS.hour()
    mins = DS.minute()
    secs = DS.second()
    until_alarm = 0
    # Special-case when the current time is already after the alarm
    if hours > alarm_hours or (hours == alarm_hours and mins > alarm_minutes) or \
            (hours == alarm_hours and mins == alarm_minutes and secs > alarm_seconds):
        until_alarm += (60 - secs)
        until_alarm += ((59 - mins) * 60)
        until_alarm += ((23 - hours) * 3600)
        until_alarm += (alarm_hours * 3600 + alarm_minutes * 60 + alarm_seconds)
    else:
        if secs > alarm_seconds:
            # Convert 1 minute to seconds to allow for easy subtraction
            if alarm_minutes > 0:
                alarm_minutes -= 1
            else:
                # No minutes available, take 1 away from hours
                if alarm_hours > 0:
                    alarm_hours -= 1
                else:
                    alarm_hours = 23
                alarm_minutes = 59
            alarm_seconds += 60
        until_alarm += (alarm_seconds - secs)
        if mins > alarm_minutes:
            # Convert 1 hour to minutes to allow for easy subtraction
            if alarm_hours > 0:
                alarm_hours -= 1
            else:
                alarm_hours = 23
            alarm_minutes += 60
        until_alarm += ((alarm_minutes - mins) * 60)
        if hours > alarm_hours:
            alarm_hours += 24
        until_alarm += ((alarm_hours - hours) * 3600)
    return until_alarm


def calculate_duty(alarm_hours, alarm_minutes, alarm_seconds):
    """Calculates LED duty based on the time until alarm"""
    time_remaining = seconds_until_alarm(alarm_hours, alarm_minutes, alarm_seconds)
    if time_remaining > (24 * 3600 - KEEP_LIGHT_ON):
        # Keep the light on after the alarm goes off
        duty = MAX_DUTY
    elif time_remaining >= SUNRISE_LENGTH:
        # Too early for the alarm
        duty = 0
    elif time_remaining >= LOW_THRESHOLD:
        # At first increase the duty mildly (linearly to LOW_THRESHOLD_DUTY)
        duty = int(LOW_THRESHOLD_DUTY * (SUNRISE_LENGTH - time_remaining) / LOW_THRESHOLD)
    else:
        # At the end increase it more quickly (linearly to DUTY_DIFF), take LOW_THRESHOLD_DUTY as a start
        duty = LOW_THRESHOLD_DUTY + int(DUTY_DIFF * (1 - time_remaining / (SUNRISE_LENGTH - LOW_THRESHOLD)))
    print("Seconds: {}, duty: {}".format(time_remaining, duty))
    return duty
    

def update_leds(alarm_hours, alarm_minutes, alarm_seconds):
    duty = calculate_duty(alarm_hours, alarm_minutes, alarm_seconds)
    for led in LEDS:
        led.duty(duty)


def connect_wifi():
    """Connects to the WI-FI"""
    with open(WIFI_FILE, 'r') as wifi:
        data = wifi.read().splitlines()
        ssid, password = data[0], data[1]
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network')
        sta_if.active(True)
        sta_if.connect(ssid, password)
        while not sta_if.isconnected():
            pass

    print('Network config:', sta_if.ifconfig())


def on_message(topic, msg):
    """Receive MQTT message, update the alarm and the storage file."""
    global ALARM_HOURS, ALARM_MINUTES, ALARM_SECONDS
    try:
        json =  loads(msg)
    except ValueError:
        print('Invalid format')
        return
    try:
        hours, minutes, seconds = json['hours'], json['minutes'], json['seconds']
        if 0 <= hours <= 23 and 0 <= minutes <= 59 and 0 <= seconds <= 59:
            ALARM_HOURS, ALARM_MINUTES, ALARM_SECONDS = hours, minutes, seconds
            with open(TIME_FILE, 'w') as outfile:
                outfile.write('{}\n{}\n{}'.format(hours, minutes, seconds))
        else:
            print('Invalid values')
            return
    except KeyError:
        print('Field not found')
        return


def epoch():
    # Convert DS.datetime() to a format used by utime.mktime
    # (year, month, day, hour, minute, second, weekday, yearday)
    t = DS.datetime()
    wd = t.pop(3)
    t.append(wd)
    t.append(1)
    return utime.mktime(t)


connect_wifi()
c = MQTTClient(CLIENT, SERVER)
c.set_callback(on_message)
c.connect()
c.subscribe(TOPIC)
update_seconds = mqtt_seconds = epoch()

try:
    while True:
        secs = epoch()
        if secs - mqtt_seconds >= 60:
            # Check MQTT message every 60 seconds
            mqtt_seconds = secs
            c.check_msg()
        if secs - update_seconds >= 1:
            # Update LED intensity every second
            update_seconds = secs
            update_leds(ALARM_HOURS, ALARM_MINUTES, ALARM_SECONDS)
        sleep(1)
finally:
    c.disconnect()
