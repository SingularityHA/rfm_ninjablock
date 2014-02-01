# SingularityHA
# Copyright (C) 2014 Internet by Design Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mosquitto
import serial
import os
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) + "/../lib")
from config import config
import state
import logging

logger = logging.getLogger(__name__)

codes = json.loads(open(os.path.dirname(os.path.realpath(__file__)) + "/codes.json", "r").read())

rfm_actuators = codes['rfm_actuators']
rfm_sensors = codes['rfm_sensors']

serialdev = str(config.get("rfm_ninjablock", "serialdev"))
broker = str(config.get("mqtt", "host"))
port = int(config.get("mqtt", "port"))

def hextobin(hexval):
        thelen = len(hexval)*4
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
	ser = serial.Serial(serialdev, 9600)  #open serial port
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
