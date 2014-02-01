import requests
import sys
import os
import ast
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) + "/../lib")
from config import config

rfm_actuators = {}
rfm_sensors = {}

def actuator_switch(name, code):
	codes = code.split("/")
	rfm_actuators["switch_" + name + "_off"] = codes[0]
	rfm_actuators["switch_" + name + "_on"] = codes[1]

def singleStateSensor(name, code):
	rfm_sensors[name] = code

picker = {
	"actuator_switch" : actuator_switch,
	"sensor_magnetic" : singleStateSensor
}

idFile = open(os.path.dirname(os.path.realpath(__file__)) + "/id.txt", "r").read()

payload = {'format': 'json', 'module': idFile}
r = json.loads(requests.get("http://" + config.get("general", "confighost") + "/api/v1/device/", params=payload).text)

for object in r['objects']:
	attrib = []
	attrib =  ast.literal_eval(object['attributes'])	
	picker[str(attrib['type']) + "_" + str(attrib['device'])](str(object['name']), str(attrib['code']))

codes = {}
codes['rfm_actuators'] = rfm_actuators
codes['rfm_sensors'] = rfm_sensors

target = open (os.path.dirname(os.path.realpath(__file__)) + "/codes.json", 'w')
target.write(json.dumps(codes))
target.close
