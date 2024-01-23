#!/usr/bin/python
import RPi.GPIO as GPIO
import time, sys
from dataclasses import dataclass

FLOW_SENSOR_GPIO = 13

GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_GPIO, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#global count
#count = 0

@dataclass
class test:
    count: int = 0
    start_counter: int = 0
    def countPulse(self, channel):
        if self.start_counter == 1:
            self.count = self.count+1

prueba = test()

GPIO.add_event_detect(FLOW_SENSOR_GPIO, GPIO.FALLpassING, callback=prueba.countPulse)

def estable(flow):
    if flow < 2:
        return "Presión baja"
    elif 2 <= flow <= 5:
        return "Presión media"
    else:
        return "Presión alta"

while True:
    try:
        prueba.start_counter = 1
        time.sleep(10)
        prueba.start_counter = 0
        flow = (prueba.count / 7.5)
        print("El flujo es: %.3f Litros/min" % (flow))

        presion = estable(flow)
        print("Estado de presión:", presion)

        prueba.count = 0
        time.sleep(5)
    except KeyboardInterrupt:
        print('\nInterrupción por teclado!')
        GPIO.cleanup()
        sys.exit()