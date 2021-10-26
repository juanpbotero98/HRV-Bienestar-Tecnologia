import argparse
import time
from pythonosc import udp_client

if __name__ == "__main__":
    # Argument Parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type = str, default="192.168.0.3", help="ip address of the server")
    parser.add_argument("--port", type=int, default=8000, help="The port the OSC server is listening on")
    parser.add_argument("--VideoActivation", type = int, default= 0, help= "HRV activation in the video section")
    parser.add_argument("--SoundActivation", type = int, default= 0, help= "HRV activation in the video section")
    args = parser.parse_args()

    # OSC Setup
    client = udp_client.SimpleUDPClient(args.ip, args.port)
    
    # Variable init
    start = [ 0, 1, 1, 1, 1]  # [Pre start, olfative, video, sound, interactive]
    hrv = [ 0, 0, args.VideoActivation, args.SoundActivation, 0] # [Pre start, olfative, video, sound, interactive]
    print(hrv)
    section_times = [10,240,240,240,240] 
    section_names = ["Pre-Start","Olfative","Video","Sound","Interactive"]
    # Main Loop
    for i in range(len(section_times)): 
        print(section_names[i])
        init_time = time.time()
        while time.time()-init_time<section_times[i]:
            client.send_message("/Start", start[i])
            client.send_message("/HRV", hrv[i])
            time.sleep(1)