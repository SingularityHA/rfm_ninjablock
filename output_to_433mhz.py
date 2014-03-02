"""
    SingularityHA RFM NinjaBlock Module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 - by Internet by Design Ltd
    :license: GPL v3, see LICENSE for more details.

"""
import mosquitto
import serial
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) + "/../lib")
from config import config
import state
import logging
import json

logger = logging.getLogger(__name__)

codes = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/codes.json", "r").read())

rfm_actuators = codes['rfm_actuators']
rfm_sensors = codes['rfm_sensors']

serialdev = str(config.get("rfm_ninjablock", "serialdev"))
broker = str(config.get("mqtt", "host"))
port = int(config.get("mqtt", "port"))


def hextobin(hexval):
    thelen = len(hexval) * 4
    binval = bin(int(hexval, 16))[2:]
    while ((len(binval)) < thelen):
        binval = '0' + binval
    return binval


def on_connect(rc):
    logger.info("Connected MQTT -> 433mhz")


def on_message(msg):
    payload = rfm_actuators[msg.payload]
    payload_split = payload.split("_")
    state.set(payload_split[0] + "." + payload_split[1], payload_split[2])
    ser = serial.Serial(serialdev, 9600)  # open serial port
    for i in range(3):
        ser.write('{"DEVICE":[{"G":"0","V":0,"D":11,"DA":"' + hextobin(payload) + '"}]}')
        time.sleep(1)
        ser.close()


def main():
    try:
        mqttc = mosquitto.Mosquitto("singularity_rfmNB_output")

        mqttc.on_message = on_message
        mqttc.on_connect = on_connect

        mqttc.connect(broker, port, 60, True)

        mqttc.subscribe("rfm_ninjablock/send", 2)

        while mqttc.loop() == 0:
            pass
    except KeyboardInterrupt:
        pass
