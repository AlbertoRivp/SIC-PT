from dataclasses import dataclass
from typing import Optional, Tuple, Union
import RPi.GPIO as GPIO
import time
import threading
from queue import Queue

def classify_presion(flow: int = 0) -> Union[float, str]:
    # TODO: Los datos no son adecuados, se necesita datos reales
    if flow == 0:
        return "Sin presión"
    elif flow < 30:
        return "Presión baja"
    elif 30 <= flow <= 60:
        return "Presión media"
    else:
        return "Presión alta"
            
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
    
    def get_presion(self) -> Tuple[float, str]:       
        self.start_counter = 1
        time.sleep(2)
        self.start_counter = 0
        flow = (self.count / 7.5)

        presion = classify_presion(flow)

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
        GPIO.setmode(GPIO.BCM)
            # Para facilitar el acceso directo a cada set de sensores, utilizaremos un diccionario
        self.sensores: dict = {}
    
    def __del__(self):
        self.stop()

    def stop(self) -> None:
        self.sensores.clear()
        GPIO.cleanup()

    def add_sensor(self, name: str, gpio_pin: int, gpio_pin_compare: int = None) -> None:
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
            # Definimos las variables de los resultados
            flow_rate_start: float = 0.0
            flow_rate_end: float = 0.0

            # Creamos funciones independientes para los hilos
            def get_flow_start():
                nonlocal medidores, flow_rate_start
                flow_start, _ = medidores[0].get_presion()
                flow_rate_start = flow_start

            def get_flow_end():
                nonlocal medidores, flow_rate_end
                flow_end, _ = medidores[1].get_presion()
                flow_rate_end = flow_end

            # Para reducir un poco el tiempo de espera, crearemos dos hilos por cada motor
            thread_flow_start = threading.Thread(target=get_flow_start)
            thread_flow_end = threading.Thread(target=get_flow_end)

            # Iniciamos la medicion
            thread_flow_start.start()
            thread_flow_end.start()

            # Esperamos a que ambos hilos terminen
            thread_flow_start.join()
            thread_flow_end.join()

            # Revisamos si ambas presiones concuerdan, con un margen de error de 10
            if flow_rate_start > flow_rate_end or flow_rate_start > (flow_rate_end + 10):
                return PresionResultados(flow_rate_start, flow_rate_end, 1)
            else:
                return PresionResultados(flow_rate_start, flow_rate_end, 0)

        elif isinstance(medidores, FlowSetup):
            flow, _ = medidores.get_presion()
            return PresionResultados(flow, None, 0)

        else:
            print(f"Warning: Unknown datatype {type(medidores)}, skipping")
            return None
    
    def remove_sensors(self, name: str) -> None:
        self.sensores.pop(name)

    def get_names(self) -> Tuple[str]:
        return tuple( self.sensores.keys() ) 
    
    def get_sensors(self, name: str):
        return self.sensores.get(name, None)
    
    def rename_sensors(self, new_name:str, old_name:str):
        if old_name in self.sensores and not new_name in self.sensores:
            self.sensores[new_name] = self.sensores.pop(old_name)
            return 1
        else:
            return 0
    