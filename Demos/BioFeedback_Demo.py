import argparse
from ast import parse
import time
from pythonosc import udp_client
import asyncio
import math
import os
import signal
import sys
from bleak import BleakClient
from bleak.uuids import uuid16_dict

#BLE Setup
uuid16_dict = {v: k for k, v in uuid16_dict.items()}

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

## UUID for Request HR data 
HR_UUID = "00002A37-0000-1000-8000-00805F9B34FB"

## Keyboard Interrupt Handler
def keyboardInterrupt_handler(signum, frame):
    print("  key board interrupt received...")
    print("----------------Recording stopped------------------------")

# OSC tranmision handler
def Send_OSC(client,HR,IBI):
    client.send_message("/IBI", IBI)
    client.send_message("/HR", HR)    

# Data container init
res = {}
res["rr"] = []
res["hr"] = []

# Hex to int conversion
def data_conv_hr(sender,data):
    """
    data is a list of integers corresponding to readings from the BLE HR monitor
    """

    byte0 = data[0]
    res["hrv_uint8"] = (byte0 & 1) == 0
    sensor_contact = (byte0 >> 1) & 3
    if sensor_contact == 2:
        res["sensor_contact"] = "No contact detected"
    elif sensor_contact == 3:
        res["sensor_contact"] = "Contact detected"
    else:
        res["sensor_contact"] = "Sensor contact not supported"
    res["ee_status"] = ((byte0 >> 3) & 1) == 1
    res["rr_interval"] = ((byte0 >> 4) & 1) == 1

    if res["hrv_uint8"]:
        res["hr"].append(data[1])
        i = 2
    else:
        res["hr"].append((data[2] << 8) | data[1])
        i = 3

    if res["ee_status"]:
        res["ee"] = (data[i + 1] << 8) | data[i]
        i += 2

    if res["rr_interval"]:
        while i < len(data):
            # Note: Need to divide the value by 1024 to get in seconds
            res["rr"].append((data[i + 1] << 8) | data[i])
            i += 2

    print("Heart Rate(bpm): {} | RR-Interval(ms): {}".format(res["hr"][-1],res["rr"]
    [-1]))
    

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
    
    # Start OSC client
    client_osc = udp_client.SimpleUDPClient(args.ip, args.port)

    # Start HR Stream
    await client.start_notify(HR_UUID, data_conv_hr)

    init_time = time.time()
    while time.time()-init_time<args.time:
        print(time.time()-init_time)
        await asyncio.sleep(1/args.interval)
        Send_OSC(client_osc,res["hr"][-1],res["rr"][-1])

async def main():
    try:
        async with BleakClient(args.mac) as client:
            signal.signal(signal.SIGINT, keyboardInterrupt_handler)
            tasks = [
                asyncio.ensure_future(run(client, True)),
            ]

            await asyncio.gather(*tasks)
    except:
        pass

if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type = str, default="192.168.1.106", help="ip address of the server")
    parser.add_argument("--mac", type = str, default="EA:F6:8F:5B:90:CF", help=" MAC ID of the sensor")
    parser.add_argument("--port", type=int, default=8000, help="The port the OSC server is listening on")
    parser.add_argument("--time",type=int,default=240,help="Duration of the Demo")
    parser.add_argument("--interval",type=int,default=2,help="Interval in which the data is being sent in seconds")
    args = parser.parse_args()

    # Main loop command
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


