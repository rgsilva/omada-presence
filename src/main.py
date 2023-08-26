#!/usr/bin/env python3

import datetime
import time
import signal
import sys

from omada import Omada
from homeassistant import HomeAssistant

from config import load_config

def _mac_to_id(mac: str) -> str:
    return mac.lower().replace("-", "")

def run(last_present: list[str] = [], last_away: list[str] = []):
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
        print("Creating", mac, config.devices[mac])
        ha.create(_mac_to_id(mac), config.devices[mac])

    present = []

    sites = omada.sites()
    for site in sites:
        clients = omada.clients(site["id"])
        for client in clients:
            lsstr = datetime.datetime.fromtimestamp(client["lastSeen"]/1000).strftime("%Y-%m-%d %H:%M:%S")
            mac_address = client["mac"]
            print(mac_address, client["name"], lsstr, end=" ")

            if mac_address not in config.devices:
                print("[unknown]")
                continue
            present.append(mac_address)
            print("[known]")

            # NOTE: hack to make it work properly.
            time.sleep(0.01)

    for mac in present:
        if mac in last_present:
            print("Already reported at home", mac)
            continue
        print("Reporting at home", mac)
        ha.set_state(_mac_to_id(mac), "home")

    missing = list(set(config.devices.keys()) - set(present))
    for mac in missing:
        if mac in last_away:
            print("Already reported away", mac)
            continue
        print("Reporting away", mac)
        ha.set_state(_mac_to_id(mac), "not_home")

    omada.logout()
    ha.disconnect()

    time.sleep(config.interval)

    return present, missing

def terminate(signal, frame):
    print("Terminating...")
    sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, terminate)

    last_present = []
    last_missing = []
    while True:
        print("-----", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----")
        last_present, last_missing = run(last_present, last_missing)
        print()
