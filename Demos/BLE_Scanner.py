import asyncio
from bleak import BleakScanner

async def main():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
    return devices

devs = asyncio.run(main())
print("finished")