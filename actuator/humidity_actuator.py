# Aktuator za vlagu
import time
import paho.mqtt.client as mqtt

ACTUATOR_TOPIC = "aktuatori/beton/vlaga/komanda"
STATE_TOPIC = "aktuatori/beton/vlaga/stanje"
HUMIDITY_FILE = "../humidity.txt"

NORMAL_HUMIDITY = 50.0  # Ciljna vrednost
STEP = 2.0              # Koliko se menja po ciklusu

class HumidityActuator:
    def __init__(self, broker_address):
        self.broker_address = broker_address
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.target = None
        self.active = False

    def on_connect(self, client, userdata, flags, rc):
        print("[AKTUATOR VLAGA] Povezan na MQTT broker!")
        client.subscribe(ACTUATOR_TOPIC)

    def on_message(self, client, userdata, msg):
        try:
            command = msg.payload.decode()
            if command == "INCREASE":
                self.target = NORMAL_HUMIDITY
                self.active = True
                print("[AKTUATOR VLAGA] Aktiviran za povećanje vlage!")
            elif command == "DECREASE":
                self.target = NORMAL_HUMIDITY
                self.active = True
                print("[AKTUATOR VLAGA] Aktiviran za smanjenje vlage!")
        except Exception as e:
            print(f"[AKTUATOR VLAGA] Greska u komandi: {e}")

    def modify_humidity(self):
        while True:
            if self.active:
                try:
                    with open(HUMIDITY_FILE, "r") as f:
                        value = float(f.read().strip())
                except Exception:
                    value = NORMAL_HUMIDITY
                if value > self.target:
                    value = max(self.target, value - STEP)
                elif value < self.target:
                    value = min(self.target, value + STEP)
                else:
                    self.active = False
                with open(HUMIDITY_FILE, "w") as f:
                    f.write(f"{value}\n")
                self.client.publish(STATE_TOPIC, f"{value}")
                print(f"[AKTUATOR VLAGA] Nova vlaga: {value}")
            time.sleep(2)

    def run(self):
        self.client.connect(self.broker_address)
        import threading
        threading.Thread(target=self.modify_humidity, daemon=True).start()
        self.client.loop_forever()

if __name__ == "__main__":
    BROKER = "localhost"
    actuator = HumidityActuator(broker_address=BROKER)
    print("[AKTUATOR VLAGA] Spreman. Čeka komande...")
    actuator.run()
