from _typeshed import Self
import time
from pythonosc import udp_client


# -------------------- OSC Communication Utils -----------------------
class OSC_CommUtils:
    def __init__(self,ip):
        self.ip = ip 
        self.port = 8000
        self.client = udp_client.SimpleUDPClient(self.ip,self.port)
    
    def tx_start(self):
        self.client.send_message("/Start", 1)
    
    def tx_standby(self):
        self.client.send_message("/Start", 0)
    
    def tx_hrv(self,ratio):
        self.client.send_message("/HRV", ratio)

