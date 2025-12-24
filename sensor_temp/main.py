
# Simulacija senzora temperature

import time
import paho.mqtt.client as mqtt
import socket
import threading


class TemperatureSensor:
    def __init__(self, sensor_id, broker_address, topic, file_path):
        self.sensor_id = sensor_id
        self.broker_address = broker_address
        self.topic = topic
        self.file_path = file_path
        self.client = mqtt.Client()
        # SSDP
        self.ssdp_port = 19001
        self.ssdp_message = f"SSDP_ANNOUNCE_TEMP:{self.sensor_id}"

    def ssdp_announce(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while True:
            sock.sendto(self.ssdp_message.encode(), ("<broadcast>", self.ssdp_port))
            time.sleep(10)

    def connect(self):
        self.client.connect(self.broker_address)

    def read_temperature(self):
        try:
            with open(self.file_path, "r") as f:
                value = float(f.read().strip())
            return value
        except Exception as e:
            print(f"Greska pri citanju temperature: {e}")
            return None

    def send_temperature(self):
        temp = self.read_temperature()
        if temp is not None:
            payload = {
                "sensor_id": self.sensor_id,
                "temperature": temp
            }
            self.client.publish(self.topic, str(payload))
            print(f"[SENT] {payload}")

    def run(self, interval=5):
        self.connect()
        print(f"Senzor {self.sensor_id} povezan na MQTT broker {self.broker_address}, tema: {self.topic}")
        threading.Thread(target=self.ssdp_announce, daemon=True).start()
        while True:
            self.send_temperature()
            time.sleep(interval)

if __name__ == "__main__":
    BROKER = "localhost"  # ili IP adresa drugog računara
    TOPIC = "senzori/beton/temperatura/vrednost"
    FILE_PATH = "../temperature.txt"
    sensor = TemperatureSensor(sensor_id="temp_1", broker_address=BROKER, topic=TOPIC, file_path=FILE_PATH)
    sensor.run(interval=5)
