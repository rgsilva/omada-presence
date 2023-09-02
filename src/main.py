#!/usr/bin/env python3

import datetime
import time
import signal
import sys

from omada import Omada
from homeassistant import HomeAssistant
from ping import is_alive

from config import load_config

def _mac_to_id(mac: str) -> str:
    return mac.lower().replace("-", "")

def run():
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

    ha.connect()
    omada.login()

    for mac in config.devices:
        print("[created]", mac, config.devices[mac])
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

            # NOTE: hack to make it work properly.
            time.sleep(0.01)

    missing = list(set(config.devices.keys()) - set(present))
    for mac in missing:
        print("[away]", mac, config.devices[mac])
        ha.set_state(_mac_to_id(mac), "not_home")

    omada.logout()
    ha.disconnect()

    time.sleep(config.interval)

def terminate(signal, frame):
    print("Terminating...")
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminate)

    while True:
        print("-----", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----")
        run()
        print()
