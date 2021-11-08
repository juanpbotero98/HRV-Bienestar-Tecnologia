import matplotlib.pyplot as plt
import time
from pythonosc import udp_client
import pyhrv
import pyhrv.frequency_domain as fd
import pyhrv.tools as tools
from pyhrv.hrv import hrv
import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog as FileDialog
from tkinter import ttk
import asyncio
from bleak import BleakScanner
from bleak.uuids import uuid16_dict

# ------------- OSC Communication Utils ----------------
class OSC_CommUtils:
    def __init__(self,ip):
        self.ip = ip 
        self.port = 8000
        self.client = udp_client.SimpleUDPClient(self.ip,self.port)
    
    def transmit(self,start_status,heart_rate,cue):
        self.client.send_message("/Start", start_status)
        self.client.send_message("/HR", heart_rate)
        self.client.send_message("/Cue", cue)     

# -------------------- HRV Utils -----------------------
class HRV_Utils:
    def HRV_plots(nni):
        # Frequency comparisson graphs
        fd.psd_comparison(nni=nni, duration=240, method='welch')
        fd.psd_waterfall(nni=nni, duration=240, method='welch')
        # Time comparisson graphs
        init_nni = nni[:240]
        final_nni = nni[1200:]
        params = ['nni_mean', 'sdnn', 'rmssd', 'nn50', 'nn20']
        tools.radar_chart(nni = init_nni, comparison_nni=final_nni, parameters=params)

    def Export_HRV(fname,export_path,nni):
        results = pyhrv.hrv(nni=nni,plot_ecg=False, plot_tachogram=False, show=False)
        plt.close('all')
        tools.hrv_export(results,efile=fname,path=export_path)

# -------------------- GUI Utils -----------------------
class GUI_Utils:
    def __init__(self,master):
        self.master = master
    
    def error_popup(self,error_msg):
        self.window = tk.Toplevel(self.master)
        self.window.title("Error")
        error_variable = tk.StringVar()
    #setting window size
        window_width=len(error_msg)*6
        window_height=80
        screenwidth = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (window_width, window_height, ((screenwidth - window_width) / 2), 
                                    (screenheight - window_height) / 2)
        self.window.geometry(alignstr)
        self.window.resizable(width=False, height=False)

    #setting title label
        Params_title=tk.Label(self.window)
        Params_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        Params_title["font"] = ft
        Params_title["fg"] = "#fbfbfb"
        Params_title["justify"] = "center"
        Params_title["text"] = "Mensaje de Error"
        Params_title["relief"] = "raised"
        Params_title.place(x=0,y=0,width=window_width,height=30)

    # setting error txt label
        Error_txtLbl=tk.Label(self.window)
        Error_txtLbl['font'] = ft
        Error_txtLbl["fg"] = "#000000"
        Error_txtLbl["justify"] = "center"
        Error_txtLbl["textvariable"] = error_variable
        Error_txtLbl.place(x=0,y=45,width=window_width,height=25)
        error_variable.set(error_msg)

class BLE_Utils:
    def __init__(self):
        
        uuid_dict = {v: k for k, v in uuid16_dict.items()}
        ## UUID for model number ##
        self.MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            uuid_dict.get("Model Number String")
        )
        ## UUID for manufacturer name ##
        self.MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            uuid_dict.get("Manufacturer Name String")
        )
        ## UUID for battery level ##
        self.BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
            uuid_dict.get("Battery Level")
        )
        ## UUID for connection establsihment with device ##
        self.PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of stream settings ##
        self.PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of start stream ##
        self.PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of ECG Stream ##
        self.ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
        # For Plolar H10  sampling frequency ##
        self.ECG_SAMPLING_FREQ = 130
        # Container for time session time and data
        self.ecg_session_data = []
        self.ecg_session_time = []

    async def scan_devices():
        devices = await BleakScanner.discover()
        for d in devices:
            print(d)
        return devices
    
