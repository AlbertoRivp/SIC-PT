from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-sensor', methods=["POST"])
def add_sensor():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)