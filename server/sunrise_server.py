import json
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request

app = Flask(__name__)
mqtt_client = mqtt.Client('web-server')
mqtt_client.connect('192.168.1.110')


def on_publish(client, userdata, result):
    print("Published data for alarm clock")


mqtt_client.on_publish = on_publish


@app.route('/alarm', methods=['POST'])
def set_alarm():
    if 'hours' not in request.form or 'minutes' not in request.form:
        return 'Not OK'
    try:
        data = {'hours': int(request.form['hours']), 'minutes': int(request.form['minutes']), 'seconds': 0}
    except ValueError:
        return 'Not OK'
    mqtt_client.publish('home/alarm', json.dumps(data))

    return 'OK'


@app.route('/')
def index():
    return render_template('clock.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
