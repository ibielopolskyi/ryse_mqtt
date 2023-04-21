import asyncio

import json
import paho.mqtt.client as paho
import os
import socket 
import sys

class HAHelper(object):
    def __init__(self, discovery_prefix=None, device_name=None):
        self.discovery_prefix = discovery_prefix
        self.name = device_name
        self.component = "cover"
        self.topic_prefix = "ryse"

    def discovery_topic(self, mac):
        return f"{self.discovery_prefix}/{self.component}/{mac.replace(':','_')}/{self.name}/config"

    def command_topic(self, mac):
        return '/'.join((self.topic_prefix, self.name, mac, "set"))

    def availability_topic(self, mac):
        return '/'.join((self.topic_prefix, self.name, mac, "availability"))

    def position_topic(self, mac):
        return '/'.join((self.topic_prefix, self.name, mac, "position"))

    def state_topic(self, mac):
        return '/'.join((self.topic_prefix, self.name, mac, "state"))

    def set_position_topic(self, mac):
        return '/'.join((self.topic_prefix, self.name, mac, "set_position"))

    def discovery_payload(self, mac, friendly_name):
        device = {
            "identifiers": self.name,
            "name": "Ryse MQTT",
            "sw_version": "0.0.2",
        }
        payload = {
            "name": friendly_name,
            "command_topic": self.command_topic(mac),
            "position_topic": self.position_topic(mac),
            "state_topic": self.state_topic(mac),
            "availability": {
                "topic": self.availability_topic(mac),
            },
            "set_position_topic": self.set_position_topic(mac),
            "qos": 0,
            "retain": True,
            "payload_open": "100",
            "invert_openclose_buttons": True,
            "payload_close": "0",
            "unique_id": mac,
            "position_open": 100,
            "state_closed": "CLOSED",
            "state_open": "OPEN",
            "state_closing": "CLOSING",
            "state_opening": "OPENING",
            "state_stopped": "STOPPED",
            "position_closed": 0,
            "payload_available": "online",
            "payload_not_available": "offline",
            "optimistic": False,
            "device": device,
        }
        return json.dumps(payload)
