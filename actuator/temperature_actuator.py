# Aktuator za temperaturu
import time
import paho.mqtt.client as mqtt

ACTUATOR_TOPIC = "aktuatori/beton/temperatura/komanda"
STATE_TOPIC = "aktuatori/beton/temperatura/stanje"
TEMP_FILE = "../temperature.txt"

NORMAL_TEMP = 20.0  # Ciljna vrednost
STEP = 1.0          # Koliko se menja po ciklusu

class TemperatureActuator:
    def __init__(self, broker_address):
        self.broker_address = broker_address
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.target = None
        self.active = False

    def on_connect(self, client, userdata, flags, rc):
        print("[AKTUATOR TEMP] Povezan na MQTT broker!")
        client.subscribe(ACTUATOR_TOPIC)

    def on_message(self, client, userdata, msg):
        try:
            command = msg.payload.decode()
            if command == "COOL":
                self.target = NORMAL_TEMP
                self.active = True
                print("[AKTUATOR TEMP] Aktiviran za hlađenje!")
            elif command == "HEAT":
                self.target = NORMAL_TEMP
                self.active = True
                print("[AKTUATOR TEMP] Aktiviran za grejanje!")
        except Exception as e:
            print(f"[AKTUATOR TEMP] Greska u komandi: {e}")

    def modify_temperature(self):
        while True:
            if self.active:
                try:
                    with open(TEMP_FILE, "r") as f:
                        value = float(f.read().strip())
                except Exception:
                    value = NORMAL_TEMP
                if value > self.target:
                    value = max(self.target, value - STEP)
                elif value < self.target:
                    value = min(self.target, value + STEP)
                else:
                    self.active = False
                with open(TEMP_FILE, "w") as f:
                    f.write(f"{value}\n")
                self.client.publish(STATE_TOPIC, f"{value}")
                print(f"[AKTUATOR TEMP] Nova temperatura: {value}")
            time.sleep(2)

    def run(self):
        self.client.connect(self.broker_address)
        import threading
        threading.Thread(target=self.modify_temperature, daemon=True).start()
        self.client.loop_forever()

if __name__ == "__main__":
    BROKER = "localhost"
    actuator = TemperatureActuator(broker_address=BROKER)
    print("[AKTUATOR TEMP] Spreman. Čeka komande...")
    actuator.run()
