import RPi.GPIO as GPIO
import time, sys


# Configura los pines GPIO para cada bomba de presión que se tenga disponible. 
# Se utiliza en conjunto con un handler
class flow_setup():
    def __init__(self, gpio_pins: list) -> None:
        # Revisamos la cantidad de pins recibida
        if len(gpio_pins) > 1:
            # Si es mayor a uno, configuramos todo con un bucle
            for pin in gpio_pins:
                GPIO.setup(pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        else:
            # De otra forma, solo extraemos el primer numero
            GPIO.setup(gpio_pins[0], GPIO.IN, pull_up_down = GPIO.PUD_UP)
