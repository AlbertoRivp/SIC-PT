from dataclasses import dataclass
from typing import Optional
import RPi.GPIO as GPIO
import time
import atexit

'''
class flow_setup():
    def __init__(self, gpio_pin_flow: int, gpio_pin_flow_compare: int = None) -> None:
        self.count: int = 0
        self.start_counter: int = 0
        self.flow: float = 0.0

        # Atributos para el segundo comparador (Puede no necesitarlos)
        self.count: int = 0
        self.start_counter: int = 0
        self.flow: float = 0.0
        # Revisamos la cantidad de pins recibida
        if gpio_pin_flow_compare:
            # Si es mayor a uno, configuramos los dos
                GPIO.setup(gpio_pin_flow, GPIO.IN, pull_up_down = GPIO.PUD_UP)
                GPIO.setup(gpio_pin_flow_compare, GPIO.IN, pull_up_down = GPIO.PUD_UP)
                # Tambien configuramos parametros extra para cada función
        else:
            # De otra forma, solo extraemos el primer numero
            GPIO.setup(gpio_pin_flow, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        

    def countPulse(self, channel):
        if self.start_counter == 1:
            self.count = self.count+1
            
    def countPulse_com(self, channel):
        if self.start_counter == 1:
            self.count = self.count+1
'''
            
class FlowSetup():
    def __init__(self, gpio_pin_flow: int) -> None:
        try:
            self.gpio_pin: int =  gpio_pin_flow
            self.count: int = 0
            self.start_counter: int = 0
            self.flow: float = 0.0
            # Configuramos el pin gpio con el pin especificado
            GPIO.setup(gpio_pin_flow, GPIO.IN, pull_up_down = GPIO.PUD_UP)

            # Iniciamos la carga del sensor
            GPIO.add_event_detect(gpio_pin_flow, GPIO.FALLING, callback=self.count_pulse)
        except Exception as e:
            raise e
    
    def __del__(self) -> None:
        self.__clean_up()

    def count_pulse(self, channel) -> None:
        if self.start_counter == 1:
            self.count = self.count+1
    
    def __clean_up(self) -> None:
        GPIO.cleanup(self.gpio_pin)

    def __classify_presion(self, flow: int = 0) -> str:
        # TODO: Los datos no son adecuados, se necesita datos reales
        if flow < 2:
            return "Presión baja"
        elif 2 <= flow <= 5:
            return "Presión media"
        else:
            return "Presión alta"
    
    def get_presion(self) -> tuple(float,str):       
        self.start_counter = 1
        time.sleep(2)
        self.start_counter = 0
        flow = (self.count / 7.5)
        print("El flujo es: %.3f Litros/min" % (flow))

        presion = self.__classify_presion(flow)
        print("Estado de presión:", presion)

        self.count = 0

        return flow, presion
    
    def get_gpio_pin(self) -> int:
        return self.gpio_pin

@dataclass
class PresionResultados:
    flow_start: float
    flow_end: float
    is_leaking: int


class FlowControl():
    def __init__(self) -> None:
        # Hacemos las debidas modificaciones al gpio para poder trabajar con BCM
        with GPIO.setmode(GPIO.BCM):
            # Para facilitar el acceso directo a cada set de sensores, utilizaremos un diccionario
            self.sensores: dict = {}
    
    @atexit.register
    def stop(self):
        self.sensores.clear()
        GPIO.cleanup()

    def add_sensor(self, name: str, gpio_pin: int, gpio_pin_compare: int = None):
        try:
            if gpio_pin_compare:
                self.sensores[name] = [FlowSetup(gpio_pin), FlowSetup(gpio_pin_compare)]
            else:
                self.sensores[name] = FlowSetup(gpio_pin)
        except Exception as e:
            print("FAIL: Unable to setup sensors")
            raise e
    

    def check_presion(self, name: str) -> Optional[PresionResultados]:
        medidores = self.sensores.get(name, None)
        if not medidores:
            return None
    
        if isinstance(medidores, list):
            flow_start, _ = medidores[0].get_presion()
            flow_end, _ = medidores[1].get_presion()
            # Revisamos si ambas presiones concuerdan, con un margen de error de 5
            if flow_start > flow_end or flow_start > (flow_end+5):
                return PresionResultados(flow_start, flow_end, 1)
            else:
                return PresionResultados(flow_start, flow_end, 0)
        
        elif isinstance(medidores, FlowSetup):
            flow = medidores.get_presion()
            return PresionResultados(flow, None, 0)

        else:
            print(f"Warning: Unknown datatype {type(medidores)}, skipping")
            return None
    
    def remove_sensors(self, name: str) -> None:
        self.sensores.pop(name)

    def get_names(self) -> list(str):
        return [ *self.sensores.keys() ] # [] crea la lista, * desempaca la lista como si introdujeramos los valores manualmente
    
    def get_sensors(self, name: str):
        return self.sensores.get(name, None)
    
