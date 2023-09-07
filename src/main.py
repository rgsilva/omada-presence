#!/usr/bin/env python3

import datetime
import time
import signal
import sys

from config import load_config, Config
from homeassistant import HomeAssistant
from omada import Omada
from ping import is_alive

def _mac_to_id(mac: str) -> str:
    return mac.lower().replace("-", "")

def _terminate(signal, frame):
    print("Terminating...")
    sys.exit()

def loop(config: Config, omada: Omada, ha: HomeAssistant):
    ha.connect()
    omada.login()

    for mac in config.devices:
        ha.create(_mac_to_id(mac), config.devices[mac])

    present = []

    sites = omada.sites()
    for site in sites:
        clients = omada.clients(site["id"])
        for client in clients:
            if client["mac"] not in config.devices:
                continue

            # TODO: use last seen.
            # last_seen = datetime.datetime.fromtimestamp(client["lastSeen"]/1000)

            ip = client["ip"] if "ip" in client else None
            client_is_alive = True
            if ip is not None:
                client_is_alive = is_alive(ip)

            if client_is_alive:
                ha.set_state(_mac_to_id(client["mac"]), "home")
                present.append(client["mac"])
                print("[at home]", client["mac"], config.devices[client["mac"]])

    missing = list(set(config.devices.keys()) - set(present))
    for mac in missing:
        print("[away]", mac, config.devices[mac])
        ha.set_state(_mac_to_id(mac), "not_home")

    omada.logout()
    ha.disconnect()

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, _terminate)

    config = load_config("config.json")

    omada = Omada(
        host=config.omada.host,
        username=config.omada.username,
        password=config.omada.password
    )
    ha = HomeAssistant(
        host=config.homeassistant.host,
        port=config.homeassistant.port,
        username=config.homeassistant.username,
        password=config.homeassistant.password
    )

    while True:
        print()
        print("-----", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----")
        loop(config, omada, ha)
        time.sleep(config.interval)
