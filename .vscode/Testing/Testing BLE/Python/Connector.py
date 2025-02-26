import asyncio
from bleak import BleakClient

async def main():
    ble_address = "28:cd:c1:0b:73:64"

    async with BleakClient(ble_address) as client:
        # we’ll do the read/write operations here
        print("Connected to BLE device")
        print(client.is_connected)        

asyncio.run(main())