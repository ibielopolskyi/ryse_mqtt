import asyncio
import configparser
import socket
import json
import sys

import asyncio_mqtt as aiomqtt

from ble_gatt import Device
from ha_helper import HAHelper


class RyseMqtt(object):
    def __init__(self, config):
        self.queue = asyncio.Queue()
        self.config = config
        self.ha = HAHelper(**config['home_assistant'])
        self.devices = []
        self.address_name_map = {}
        for friendly_name, address in config['ryse'].items():
            self.devices.append(Device(address, self.queue, config['fast'].get(friendly_name)))
            self.address_name_map[address] = friendly_name

    async def queue_drain(self):
        async with aiomqtt.Client(**self.config['mqtt']) as mqtt_client:
            while True:
                address, event = await self.queue.get()
                print("Got BT message", address, event)
                self.queue.task_done()
                if event == "discover":
                    await mqtt_client.publish(self.ha.discovery_topic(address), self.ha.discovery_payload(address, self.address_name_map[address]))
                elif event in ("online", "offline"):
                    await mqtt_client.publish(self.ha.availability_topic(address), event)
                elif isinstance(event, int):
                    await mqtt_client.publish(self.ha.position_topic(address), event)
                else:
                    await mqtt_client.publish(self.ha.state_topic(address), event)

    async def listen(self):
        async with aiomqtt.Client(**self.config['mqtt']) as client:
            async with client.messages() as messages:
                await client.subscribe("ryse/+/+/set_position")
                await client.subscribe("ryse/+/+/set")
                async for message in messages:
                    for device in self.devices:
                        if device.address in str(message.topic):
                            try:
                                await device.cmd(int(message.payload.decode('utf-8')))
                            except Exception as e:
                                pass

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            bt_tasks = []
            print(self.devices)
            mqtt = loop.create_task(self.listen())
            for device in self.devices:
               bt_tasks.append(loop.create_task(device.connection_loop()))
            drain = loop.create_task(self.queue_drain())
            tasks = asyncio.gather(
                mqtt, drain, *bt_tasks
            )
            loop.run_until_complete(tasks)
        except:
            import traceback
            traceback.print_exc()
            loop.create_task(
                evice.client.disconnect() 
                for device in self.devices
                if device.client.is_connected
            )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = "config.conf"

    config = configparser.ConfigParser()
    config.read(config_path)
    ryse_mqtt = RyseMqtt(config)
    ryse_mqtt.run()