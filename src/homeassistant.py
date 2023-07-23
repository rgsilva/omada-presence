import json
import paho.mqtt.client as mqtt

class HomeAssistant:
    def __init__(self, host: str, port: int, username: str, password: str):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._client = mqtt.Client()
        self._client.username_pw_set(self._username, self._password)

    def connect(self):
        self._client.connect(host=self._host, port=self._port)
    
    def disconnect(self):
        self._client.disconnect()

    def create(self, id: str, name: str):
        config = {
            "state_topic": f"{id}/state",
            "name": name,
            "payload_home": "home",
            "payload_not_home": "not_home"
        }
        self._client.publish(f"homeassistant/device_tracker/{id}/config", json.dumps(config))

    def set_state(self, id: str, state: str):
        self._client.publish(f"{id}/state", state)
