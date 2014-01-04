# Actuator Functions
def switch(dev, intent, data = None):
        if intent == "on":
                print  "switch_"+ dev +"_on"
                mqttc.publish("rfm_ninjablock/send", "switch_"+ str(dev) +"_on" )
        if intent == "off":
                mqttc.publish("rfm_ninjablock/send", "switch_"+ str(dev) +"_off" )
