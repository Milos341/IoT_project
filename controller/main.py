# Centralni kontroler
import paho.mqtt.client as mqtt
import json

import socket
import threading

TEMP_TOPIC = "senzori/beton/temperatura/vrednost"
HUMIDITY_TOPIC = "senzori/beton/vlaga/nivo"
TEMP_ACTUATOR_CMD = "aktuatori/beton/temperatura/komanda"
HUMIDITY_ACTUATOR_CMD = "aktuatori/beton/vlaga/komanda"
TEMP_LIMIT_HIGH = 35.0
TEMP_LIMIT_LOW = 5.0
HUMIDITY_LIMIT_HIGH = 70.0
HUMIDITY_LIMIT_LOW = 30.0

class Controller:
    def __init__(self, broker_address):
        self.broker_address = broker_address
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.data = []  # Lista za skladištenje primljenih podataka
        # SSDP
        self.ssdp_port = 19001
        self.discovered_sensors = set()

    def on_connect(self, client, userdata, flags, rc):
        print("Povezan na MQTT broker!")
        client.subscribe([(TEMP_TOPIC, 0), (HUMIDITY_TOPIC, 0)])

    def on_message(self, client, userdata, msg):
        try:
            payload = eval(msg.payload.decode())  # Pretpostavlja se da je payload dict kao string
        except Exception as e:
            print(f"Greska u dekodiranju poruke: {e}")
            return
        print(f"[RECEIVED] {msg.topic}: {payload}")
        self.data.append({"topic": msg.topic, **payload})
        # Provera granica i slanje komandi aktuatorima
        if msg.topic == TEMP_TOPIC:
            temp = payload.get("temperature", 0)
            if temp > TEMP_LIMIT_HIGH:
                self.send_temp_actuator("COOL")
            elif temp < TEMP_LIMIT_LOW:
                self.send_temp_actuator("HEAT")
        if msg.topic == HUMIDITY_TOPIC:
            humidity = payload.get("humidity", 0)
            if humidity > HUMIDITY_LIMIT_HIGH:
                self.send_humidity_actuator("DECREASE")
            elif humidity < HUMIDITY_LIMIT_LOW:
                self.send_humidity_actuator("INCREASE")

    def send_temp_actuator(self, command):
        print(f"[KOMANDA TEMP AKTUATORU] {command}")
        self.client.publish(TEMP_ACTUATOR_CMD, command)

    def send_humidity_actuator(self, command):
        print(f"[KOMANDA VLAGA AKTUATORU] {command}")
        self.client.publish(HUMIDITY_ACTUATOR_CMD, command)

    def run(self):
        # Pokreni SSDP listener u posebnoj niti
        threading.Thread(target=self.ssdp_listener, daemon=True).start()
        self.client.connect(self.broker_address)
        self.client.loop_forever()

    def ssdp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", self.ssdp_port))
        print(f"[SSDP] Slušam SSDP poruke na portu {self.ssdp_port}...")
        while True:
            data, addr = sock.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("SSDP_ANNOUNCE_"):
                if msg not in self.discovered_sensors:
                    self.discovered_sensors.add(msg)
                    print(f"[SSDP] Pronađen senzor: {msg} sa {addr[0]}")

if __name__ == "__main__":
    BROKER = "localhost"  # ili IP adresa brokera
    controller = Controller(broker_address=BROKER)
    print("Kontroler spreman. Čeka podatke sa senzora...")
    controller.run()
