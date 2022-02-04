import asyncio
import math
import os
import signal
import sys
import time

import pandas as pd
from bleak import BleakClient
from bleak.uuids import uuid16_dict
import matplotlib.pyplot as plt
import matplotlib


""" Predefined UUID (Universal Unique Identifier) mapping are based on Heart Rate GATT service Protocol that most
Fitness/Heart Rate device manufacturer follow (Polar H10 in this case) to obtain a specific response input from
the device acting as an API """

uuid16_dict = {v: k for k, v in uuid16_dict.items()}

## This is the device MAC ID, please update with your device ID
ADDRESS = "D6:A2:92:60:A9:FB"

## UUID for model number ##
MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Model Number String")
)


## UUID for manufacturer name ##
MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Manufacturer Name String")
)

## UUID for battery level ##
BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)

## UUID for connection establsihment with device ##
PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of stream settings ##
PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request of start stream ##
PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"

## UUID for Request HR data 
HR_UUID = "00002A37-0000-1000-8000-00805F9B34FB" 

## UUID for Request of ECG Stream ##
ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
IBI_SET = bytearray([0x01, 0x01])

def data_conv(sender, data):
    print(', '.join('{:02x}'.format(x) for x in data))

## Keyboard Interrupt Handler
def keyboardInterrupt_handler(signum, frame):
    print("  key board interrupt received...")
    print("----------------Recording stopped------------------------")

async def run(client, debug=False):

    ## Writing chracterstic description to control point for request of UUID (defined above) ##

    await client.is_connected()
    print("---------Device connected--------------")

    model_number = await client.read_gatt_char(MODEL_NBR_UUID)
    print("Model Number: {0}".format("".join(map(chr, model_number))))

    manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
    print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

    battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
    print("Battery Level: {0}%".format(int(battery_level[0])))

    att_read = await client.read_gatt_char(PMD_CONTROL)
    print(att_read)


    ## ATTRUBUTE stream started
    # await client.start_notify(PMD_CONTROL, data_conv)
    # await client.write_gatt_char(PMD_CONTROL, IBI_SET,response=True)

    # init_time = time.time()
    # start_hex = 0x00
    # end_hex = 0xff
    # for i in range(start_hex,end_hex):
    #     WRITE = bytearray([0x01, i])
    #     await client.write_gatt_char(PMD_CONTROL, WRITE,response=True)
    #     await asyncio.sleep(1)
    # await client.stop_notify(PMD_DATA)

    await client.start_notify(HR_UUID, data_conv)

    init_time = time.time()
    while time.time()-init_time<40:
        print(time.time()-init_time)
        await asyncio.sleep(1)
    
    
    print("Stopping ECG data...")
    print("[CLOSED] application closed.")
    # print(ecg_session_data)
    # ax.plot(ecg_session_data)
    # plt.show(block=False)
    sys.exit(0)

async def main():
    try:
        async with BleakClient(ADDRESS) as client:
            signal.signal(signal.SIGINT, keyboardInterrupt_handler)
            tasks = [
                asyncio.ensure_future(run(client, True)),
            ]

            await asyncio.gather(*tasks)
    except:
        pass


if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())