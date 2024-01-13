#!/usr/bin/python
import RPi.GPIO as GPIO
import time, sys

FLOW_SENSOR_GPIO = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

global count
count = 0

def countPulse(channel):
   global count
   if start_counter == 1:
      count = count+1

GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLING, callback=countPulse)

def estable(flow):
    if flow < 2:
        return "Presión baja"
    elif 2 <= flow <= 5:
        return "Presión media"
    else:
        return "Presión alta"

while True:
    try:
        start_counter = 1
        time.sleep(1)
        start_counter = 0
        flow = (count / 7.5)
        print("El flujo es: %.3f Litros/min" % (flow))

        presion = estable(flow)
        print("Estado de presión:", presion)

        count = 0
        time.sleep(5)
    except KeyboardInterrupt:
        print('\nInterrupción por teclado!')
        GPIO.cleanup()
        sys.exit()