import asyncio

from bleak import BleakClient
from bleak import BleakScanner
from bleak import BleakGATTCharacteristic

bluez_lock = asyncio.Lock()

class Device(object):
    def __init__(self, address, queue, fast):
        self.fast = fast
        self.queue = queue
        self.connection_enabled = False
        self.address = address
        self.client = BleakClient(self.address, disconnected_callback=self.on_disconnect)
        self.state = "STOPPED"
        self.position = 0
        self.tx = "a72f2802-b0bd-498b-b4cd-4a3901388238"
        self.rx = "a72f2801-b0bd-498b-b4cd-4a3901388238"

    def set_position(self, i):
        return [245, 3, 1, 1, i, i + 2]

    def update_state(self, value):
        for b in value:
            print(b, end=' ')
        
        if (int(value[5]) == 0):
            self.moving = False
        if (int(value[5]) == 1):
            self.state = "OPENING"
            self.moving = True
        if (int(value[5]) == 2):
            self.state = "CLOSING"
            self.moving = True
        if not self.moving:
            self.state = "STOPPED"
        if not self.moving and int(value[4]) == 0:
            self.state = "OPEN"
        if not self.moving and int(value[4]) == 100:
            self.state = "CLOSED"
        self.position = 100 - int(value[4])

    def callback(self, sender, data: bytearray):
        self.update_state(data)
        self.queue.put_nowait((self.address, self.state))
        if not self.moving:
            self.queue.put_nowait((self.address, self.position))

    def on_disconnect(self, client):
        print('Disconnected')
        self.queue.put_nowait((self.address, "offline"))


    async def cmd(self, cmd):
        if not self.client.is_connected:
            await self.connect()
        await self.client.write_gatt_char(self.tx, self.set_position(100 - cmd))

    async def connect(self):
        await self.queue.put((self.address, "offline"))
        if not self.client.is_connected:
            async with bluez_lock:
                await self.client.connect()
            self.connected = self.client.is_connected
            if self.connected:
                await self.queue.put((self.address, "online"))

            self.callback(self.rx, await self.client.read_gatt_char(self.rx))
            await self.client.start_notify(
                self.rx, self.callback,
            )

    async def connection_loop(self):
        await self.queue.put((self.address, "discover"))
        while True:
            try:
                if not self.client.is_connected and self.fast:
                    await self.connect()
                else:
                    await asyncio.sleep(1.0)
            except Exception as e:
                print(e)
                await asyncio.sleep(1.0)



    