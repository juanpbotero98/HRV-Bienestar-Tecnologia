import argparse
import random
import time

from pythonosc import udp_client


# if __name__ == "__main__":
#   parser = argparse.ArgumentParser()
#   parser.add_argument("--ip", default="127.0.0.1",
#       help="The ip of the OSC server")
#   parser.add_argument("--port", type=int, default=5005,
#       help="The port the OSC server is listening on")
#   args = parser.parse_args()

ip = "192.168.0.3"
port = 8000
client = udp_client.SimpleUDPClient(ip,port) #(args.ip, args.port)

for x in range(100):
    if x == 1:
        client.send_message("/Start", 1)
    client.send_message("/HRV", random.random())    
    time.sleep(10)