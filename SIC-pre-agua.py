from flask import Flask, render_template, redirect, flash, request, url_for
from sensores import FlowControl, PresionResultados, classify_presion


app = Flask(__name__)
flow_ctl = FlowControl()

app.jinja_env.globals.update(classify_presion=classify_presion)

@app.route('/')
def index():
    names = flow_ctl.get_names()
    values: list = []
    for name in names:
        values.append(flow_ctl.check_presion(name))
    return render_template('index.html', values=zip(names, values))

@app.route('/add-sensor', methods=["POST"])
def add_sensor():
    setup_form = request.form
    sensors_name = setup_form.get('set-name')
    sensors_flow_start_gpio = int(setup_form.get('gpio_pin_start'))
    if setup_form.get('has_second_sensor'):
        sensors_flow_end_gpio = int(setup_form.get('gpio_pin_end'))
    else:
        sensors_flow_end_gpio = None

    try:
        flow_ctl.add_sensor(sensors_name, sensors_flow_start_gpio, sensors_flow_end_gpio)
        flash("Se ha agregado con exito los sensores", "info")
    except Exception as e:
        flash(f"No se pudo configurar los sensores solicitados: {e}", "error")
    finally:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)