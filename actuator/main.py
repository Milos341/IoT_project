# Modul za simulaciju aktuatora
import paho.mqtt.client as mqtt

ACTUATOR_TOPIC = "system/actuator"

class Actuator:
    def __init__(self, broker_address):
        self.broker_address = broker_address
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Aktuator povezan na MQTT broker!")
        client.subscribe(ACTUATOR_TOPIC)

    def on_message(self, client, userdata, msg):
        print(f"[AKCIJA] Aktuator izvršava: {msg.payload.decode()}")

    def run(self):
        self.client.connect(self.broker_address)
        self.client.loop_forever()

if __name__ == "__main__":
    BROKER = "localhost"  # ili IP adresa brokera
    actuator = Actuator(broker_address=BROKER)
    print("Aktuator spreman. Čeka komande...")
    actuator.run()
