import sqlite3 as sql
from datetime import datetime
from sensores import FlowControl, PresionResultados
from time import sleep
from threading import Lock

# Clase para guardar en la base de datos mediciones de presion cada 30 minutos
class AguaTranquilasDBThread():
    # Espera un tipo de objeto FlowControl ya inicializado y un lock el cual permitira sincronizar el uso de los sensores
    def __init__(self, flow_ctl: FlowControl, lock: Lock) -> None:
        self.flow_ctl = flow_ctl
        self.lock = lock

    # Guarda en la base de datos cada 30 minutos. Utiliza Locks para tomar turnos para usar los sensores
    def save_to_bd(self):
        while True:
            names = self.flow_ctl.get_names()
            for name in names:
                print(f"[DATABASE] Saving {name}")
                with self.lock:
                    datos: PresionResultados = self.flow_ctl.check_presion(name)
                if datos:
                    # Saltamos si ocurre un problema con los nombres de tablas
                    try:
                        insertar_Datos(name, name, datos.flow_start)
                    except:
                        continue
            sleep(30*60) # Esperar cada 30 minutos (30 veces * 60 segundos) para guardar la informacion
            
# Crea la base de datos
def createDB():
    #Creacion de la base de datos
    conn = sql.connect("AguaTranquilas.db")
    # Guardar (commit) los cambios
    conn.commit()
    conn.close()

# Crea una tabla en base al nombre de la tuberia, esta almacena el nombre, fecha de captura y la presion
def createTabla(nombre_tabla):
    conn = sql.connect("AguaTranquilas.db")
    cursor = conn.cursor()
    cursor.execute(f'''CREATE TABLE IF NOT EXISTS {nombre_tabla}(
                   nombre varchar(17),
                   fecha DATETIME DEFAULT CURRENT_DATE,
                   presion REAL)  ''')
    conn.commit()
    conn.close()

# Renombra una tabla especificada
def renameTabla(nuevo_nombre: str, viejo_nombre: str):
    conn = sql.connect("AguaTranquilas.db")
    cursor = conn.cursor()
    cursor.execute(f'ALTER TABLE {viejo_nombre} RENAME TO {nuevo_nombre}')
    conn.commit()
    conn.close()

# Retorna las configuraciones de los sensores, a manera de backup
def createTablaSensores():
    conn = sql.connect("AguaTranquilas.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensoresInfo(
                   nombre varchar(17),
                   gpio_pin_flow_in INTEGER,
                   gpio_pin_flow_out INTEGER)
                   ''')
    conn.commit()
    conn.close()

def insertar_Datos(nombre_tabla, nombre, presion):
    # Conexion de base de datos
    conn = sql.connect("AguaTranquilas.db")
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Obtener la fecha y hora actual formateada como string
    fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insertar datos en la tabla especificada, incluyendo la fecha y hora de registro actual
    cursor.execute(f'INSERT INTO {nombre_tabla} (nombre, fecha, presion) VALUES (?, ?, ?)', (nombre,fecha_hora_actual, presion))

    # Guardar (commit) los cambios
    conn.commit()
    conn.close

def agregarSensores(nombre: str, gpio_pin_flow_in: int, gpio_pin_flow_out:int = None):
    # Conexion de base de datos
    conn = sql.connect("AguaTranquilas.db")
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Insertar datos en la tabla especificada, incluyendo la fecha y hora de registro actual
    cursor.execute(f'''INSERT INTO sensoresInfo(nombre, gpio_pin_flow_in, gpio_pin_flow_out)
                    VALUES (?, ?, ?)''', (nombre,gpio_pin_flow_in, gpio_pin_flow_out))

    # Guardar (commit) los cambios
    conn.commit()
    conn.close

# Retorna las configuraciones de los sensores, a manera de backup
def recoverSensores() -> list[str]:
    conn = sql.connect("AguaTranquilas.db")
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Consultar datos de la tabla especificada
    cursor.execute('SELECT * FROM sensoresInfo')
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_datos_de_tablas(nombre_tabla):
    # Conexión a la base de datos
    conn = sql.connect("AguaTranquilas.db")
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Consultar datos de la tabla especificada
    cursor.execute('SELECT * FROM {}'.format(nombre_tabla))
    datos = cursor.fetchall()

    # Cerrar la conexión
    conn.close()

    return datos

def ver_datos(nombre_tabla):
    # Conexión a la base de datos
    conn = sql.connect("AguaTranquilas.db")
    # Crear un cursor para ejecutar comandos SQL
    cursor = conn.cursor()

    # Consultar datos de la tabla especificada
    cursor.execute('SELECT * FROM {}'.format(nombre_tabla))
    datos = cursor.fetchall()

    # Mostrar los datos
    print(f"Datos de la tabla {nombre_tabla}:")
    for dato in datos:
        print(dato)

    # Cerrar la conexión
    conn.close()