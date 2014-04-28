"""
    SingularityHA RFM NinjaBlock Module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2013 - by Internet by Design Ltd
    :license: GPL v3, see LICENSE for more details.

"""
import serial
import mosquitto
import os
import time
import calendar
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) + "/../lib")
from config import config
import logging

codes = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/codes.json", "r").read())

rfm_actuators = codes['rfm_actuators']
rfm_sensors = codes['rfm_sensors']

logger = logging.getLogger(__name__)

serialdev = str(config.get("rfm_ninjablock", "serialdev"))
broker = str(config.get("mqtt", "host"))
port = int(config.get("mqtt", "port"))


def rfm():
    logger.debug("433mhz")


def humidity():
    logger.debug("H")


def temperature():
    logger.debug("T")


def undef():
    logger.debug("Ignore")


device_id = {11: rfm,
             30: humidity,
             31: temperature,
             999: undef,
             1007: undef,
}


def on_publish(val):
    logger.debug("Published 433mhz")


def cleanup():
    logger.info("Ending and cleaning up")
    try:
        ser.close()
        mqttc.disconnect()
    except NameError:
        pass


def main():
    try:
        logger.debug("Connecting to serial port. ")
        ser = serial.Serial(serialdev, 9600, timeout=20)
    except:
        logger.debug("Failed to connect serial")
        raise SystemExit

    try:
        ser.flushInput()
        client = "singularity_rfmNB_input"
        mqttc = mosquitto.Mosquitto(client)

        mqttc.on_publish = on_publish
        mqttc.connect(broker, port, 60, True)

        lastline = None
        lastpublish = 0

        while mqttc.loop() == 0:
	    time.sleep(0.01)
            line = ser.readline()
            gap = calendar.timegm(time.gmtime()) - lastpublish
            try:
                data = json.loads(line)
                logger.debug(data)
                try:
                    device_id[data['DEVICE'][0]['D']]()
                    if data['DEVICE'][0]['D'] == 11:
			logger.debug("sensor hex " + str(hex(int(data['DEVICE'][0]['DA'], 2))))
                        result = rfm_sensors[hex(int(data['DEVICE'][0]['DA'], 2))]
			logger.debug(rfm_sensors)
			logger.debug(result)
                        json_data = json.dumps([result])
                        if gap < 10:
                            if line == lastline:
                                pass
                            else:
                                mqttc.publish("sensors", json_data)
                                lastpublish = calendar.timegm(time.gmtime())
                                logger.debug(hex(int(data['DEVICE'][0]['DA'], 2)))
                        else:
                            logger.debug(hex(int(data['DEVICE'][0]['DA'], 2)))
                            mqttc.publish("sensors", json_data)
                            lastpublish = calendar.timegm(time.gmtime())
                        lastline = line
                    else:
                        logger.info("Other sensors - not implemented")
                except KeyError:
                    pass
            except ValueError:
                logger.info("Invalid JSON")

            pass

    except IndexError:
        logger.debug("No data received within serial timeout period")
        cleanup()
    except KeyboardInterrupt:
        logger.debug("Interrupt received")
        cleanup()
    except RuntimeError:
        logger.debug("uh-oh! time to die")
        cleanup()
