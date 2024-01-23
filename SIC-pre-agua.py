from flask import Flask, render_template, redirect, flash, request, url_for
from sensores import FlowControl, PresionResultados


app = Flask(__name__)
flow_ctl = FlowControl()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-sensor', methods=["POST"])
def add_sensor():
    error: str = None
    setup_form = request.form
    sensors_name = setup_form.get('name')
    sensors_flow_start_gpio = setup_form.get('gpio_pin_start')
    if setup_form.get('has_second_sensor'):
        sensors_flow_end_gpio = setup_form.get('gpio_pin_end')
    else:
        sensors_flow_end_gpio = None

    try:
        flow_ctl.add_sensor(sensors_name, sensors_flow_start_gpio, sensors_flow_end_gpio)
        flash("Se ha agregado con exito los sensores")
    except Exception as e:
        error = f"No se pudo configurar los sensores solicitados: {e}"
    finally:
        return redirect('/', error=error)

if __name__ == '__main__':
    app.run(debug=True)