from flask import Flask, render_template, redirect, flash, request
from sensores import FlowControl, PresionResultados, classify_presion
import aguasTranquilas_sqlite as db
import threading

app = Flask(__name__)
flow_ctl = FlowControl()

# Pasamos la funcion 'classify_presion' a jinja para poder usarlo en el template
app.jinja_env.globals.update(classify_presion=classify_presion)

# Lock para hacer que la base de datos espere a que flask termine de usar los sensores
database_lock = threading.Lock()

# El index de la pagina. 
@app.route('/')
def index():
    # Bloqueamos la base de datos para evitar que acceda a los sensores
    with database_lock:
        # Obtenemos los nombres registrados
        names = flow_ctl.get_names()
        # Definimos variables para guardar informacion de los sensores y la base de datos respectivamente
        data: list = []
        db_datos: list = []
        for name in names:
            # Obtenemos información
            data.append(flow_ctl.check_presion(name))
            db_datos.append(db.obtener_datos_de_tablas(name))
    # Guardamos nuestros datos en una lista para usarlos en el template
    values= list(zip(names,data))
    # Retornamos el template 'index.html' junto a las variables 'values' y 'inicio_tabla'
    return render_template('index.html', values=values, inicio_tabla=db_datos)

@app.route('/add_sensor', methods=["POST"])
def add_sensor():
    # Bloqueamos la base de datos para evitar que acceda a los sensores
    with database_lock:
        # Obtenemos el formulario para agregar los sensores
        setup_form = request.form
        sensors_name = setup_form.get('set-name')
        sensors_flow_start_gpio = int(setup_form.get('gpio_pin_start'))
        # Si se habilito la casilla para agregar un sensor de salida, se verifica y se obtiene el pin
        if setup_form.get('has_second_sensor'):
            sensors_flow_end_gpio = int(setup_form.get('gpio_pin_end'))
        else:
            sensors_flow_end_gpio = None

        try:
            # Agregamos los sensores para registrarlos en FlowControl y asi poder obtener resultados
            flow_ctl.add_sensor(sensors_name, sensors_flow_start_gpio, sensors_flow_end_gpio)
            # Creamos la tabla dentro de la base de datos para empezar a guardar información
            db.createTabla(sensors_name)
            flash("Se ha agregado con exito los sensores", "info")
            # Agregamos los datos de los sensores a la tabla de registro de sensores
            db.agregarSensores(sensors_name, sensors_flow_start_gpio, sensors_flow_end_gpio)
            
        except Exception as e:
            flash(f"No se pudo configurar los sensores solicitados: {e}", "error")
        finally:
            return redirect('/')

# Permite renombrar los sensores
@app.route('/rename_sensor', methods=["POST"])
def rename_sensor():
    # Bloqueamos la base de datos para evitar que acceda a los sensores
    with database_lock:
        # Obtenemos el formulario, junto a eso el nombre nuevo y viejo de los sensores
        setup_form = request.form
        sensors_name = setup_form.get('set-name')
        old_sensors_name = setup_form.get('old-name')
        # Si el FlowControl encontro el viejo nombre, y el nuevo no existe todavía, entonces procede a rescribirlo
        if flow_ctl.rename_sensors(sensors_name, old_sensors_name):
            db.renameTabla(sensors_name, old_sensors_name)
        else:
            flash("No se encontro dicha tuberia", "error")
    return redirect('/')

if __name__ == '__main__':
    #db.createTablaSensores()
    try:
        # Creamos el objeto para guardar los registros cada 30 minutos
        database = db.AguaTranquilasDBThread(flow_ctl, database_lock)
        # Registramos el thread y habilitamos 'daemon' para que finalice junto con el hilo padre
        thread_database = threading.Thread(target=database.save_to_bd)
        thread_database.daemon = True
        # Iniciamos el hilo
        thread_database.start()
        # Iniciamos flask
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        # Esperamos a que termine el hilo de la base de datos
        thread_database.join()
        exit()
    
    