#!/usr/bin/env python3

import datetime
import json
import time

from omada import Omada
from homeassistant import HomeAssistant

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
        print("Creating", mac, config.devices[mac])
        ha.create(_mac_to_id(mac), config.devices[mac])

    present = []

    sites = omada.sites()
    for site in sites:
        clients = omada.clients(site["id"])
        for client in clients:
            lsstr = datetime.datetime.fromtimestamp(client["lastSeen"]/1000).strftime("%Y-%m-%d %H:%M:%S")
            print(client["mac"], client["name"], lsstr, end=" ")

            if client["mac"] not in config.devices:
                print("[unknown]")
                continue
            present.append(client["mac"])

            print("[updated]")
            ha.set_state(_mac_to_id(client["mac"]), "home")

    missing = list(set(present) - set(config.devices.keys()))
    for mac in missing:
        ha.set_state(_mac_to_id(mac), "not_home")

    omada.logout()
    ha.disconnect()

    time.sleep(config.interval)

while True:
    print("-----", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "-----")
    run()
    print()
