import argparse
import time
from pythonosc import udp_client
from random import randint

if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type = str, default="192.168.0.3", help="ip address of the server")
    parser.add_argument("--port", type=int, default=8000, help="The port the OSC server is listening on")
    parser.add_argument("--time",type=int,default=240,help="Duration of the Demo")
    parser.add_argument("--interval",type=float,default=1.0,help="Interval in which the data is being sent in seconds")
    args = parser.parse_args()

    # OSC Setup
    client = udp_client.SimpleUDPClient(args.ip, args.port)
    
    # # Variable init
    # start = [ 0, 1, 1, 1, 1]  # [Pre start, olfative, video, sound, interactive]
    # hrv = [ 0, 0, args.VideoActivation, args.SoundActivation, 0] # [Pre start, olfative, video, sound, interactive]
    # print(hrv)
    # section_times = [10,240,240,240,240] 
    # section_names = ["Pre-Start","Olfative","Video","Sound","Interactive"]
    # Main Loop
    init_time = time.time()
    while time.time()-init_time<args.time:
        HR = randint(80,90)
        IBI = randint(800,1000)
        client.send_message("/HR", HR)
        client.send_message("/IBI", IBI)
        time.sleep(args.interval)