# Read the current state of a characteristic on a BLE device

import asyncio
from bleak import BleakClient

async def main():
    ble_address = "28:cd:c1:0b:73:64"
    characteristic_uuid = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

    while True:
        async with BleakClient(ble_address) as client:
            data = await client.read_gatt_char(characteristic_uuid)
            print(data)
        await asyncio.sleep(1)

asyncio.run(main())