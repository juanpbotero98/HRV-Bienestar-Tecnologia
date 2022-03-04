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
import biosppy
import csv 
import os

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
        # print(" {}, {}, {}".format(start_status,cue,heart_rate))     

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

    def Export_HRV(fname,export_path,ecg):
        loaded_ecg= biosppy.signals.ecg.ecg(ecg,sampling_rate=130,show = False)
        plt.close('all') 
        IBI = []
        for i in range(len(loaded_ecg[2])-1):
            IBI.append(loaded_ecg[0][loaded_ecg[2][i+1]]-loaded_ecg[0][loaded_ecg[2][i]])

        results = pyhrv.hrv(nni=IBI,plot_ecg=False, plot_tachogram=False, show=False)
        plt.close('all')
        tools.hrv_export(results,efile=fname,path=export_path)
    
    def Save_ECG(ecg,finnished,export_path):
        row_names = ['ECG raw', 'ECG Filtrado','Tiempo (s)', 'Ritmo Cardiaco', 'Picos R-R', 'IBI Serie']
        fnames = ['ECG_baseline','ECG_olfative','ECG_sound','ECG_video','ECG_interactive','ECG_final']
        # writer = csv.DictWriter(file,fieldnames=fnames)
        # writer.writeheader()
        for i in range(len(ecg)):
            file_path = os.path.join(export_path,fnames[i]+'.csv')
            image_path = os.path.join(export_path,fnames[i])
            with open(file_path,mode='w') as file:
                writer = csv.writer(file)
                loaded_ecg= biosppy.signals.ecg.ecg(ecg[i][0],sampling_rate=130,path=image_path)
                plt.close('all')    
                # Get Heart Rate data
                HR_data = loaded_ecg[5].tolist()
                HR_data.insert(0,'Heart Rate')

                # Get time axis
                time_ref =  loaded_ecg[0].tolist()
                time_ref.insert(0,'Time (s)')

                # Get filtered ECG
                filtered_ecg = loaded_ecg[1].tolist()
                filtered_ecg.insert(0,'ECG')

                # Get R-peaks series using biosppy
                rpeaks = loaded_ecg[2]
                
                # Compute NNI series
                nni = tools.nn_intervals(rpeaks).tolist()
                rpeaks = rpeaks.tolist()
                rpeaks.insert(0,'Rpeaks')
                
                
                
                nni.insert(0,'IBI Series')

                # Write file 
                writer.writerow(filtered_ecg)
                writer.writerow(time_ref)
                writer.writerow(rpeaks)
                writer.writerow(nni)
                writer.writerow(HR_data)
        # Save all data 

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
        ft = tkFont.Font(family='Times.csv',size=10)
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
    
class OperationModes_Popup():

    def __init__(self, master):
        self.master = master

    def popup(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("Modos de Operación")
        self.finished_flag = False

    #setting window size
        window_width=180
        window_height=190
        screenwidth = self.master.winfo_screenwidth()
        screenheight = self.master.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (window_width, window_height, ((screenwidth - window_width) / 2)+400, 
                                    (screenheight - window_height) / 2)
        self.window.geometry(alignstr)
        self.window.resizable(width=False, height=False)

    #setting title label
        OpModes_title=tk.Label(self.window)
        OpModes_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        OpModes_title["font"] = ft
        OpModes_title["fg"] = "#fbfbfb"
        OpModes_title["justify"] = "center"
        OpModes_title["text"] = "Modos de Operación"
        OpModes_title["relief"] = "raised"
        OpModes_title.place(x=0,y=0,width=180,height=30)

    #setting Control Group OP Mode check box
        self.ControlGroup = tk.BooleanVar()
        self.ControlGroup_chkBox = tk.Checkbutton(self.window)
        self.ControlGroup_chkBox["justify"] = "left"
        self.ControlGroup_chkBox["anchor"] = "w"
        self.ControlGroup_chkBox["text"] = 'Grupo Control'
        self.ControlGroup_chkBox["variable"] = self.ControlGroup
        self.ControlGroup_chkBox["onvalue"] = True
        self.ControlGroup_chkBox["offvalue"] = False
        self.ControlGroup_chkBox.place(x=0,y=40,width=170,height = 25)

    #setting test mode check box
        self.TestMode = tk.BooleanVar()
        self.TestMode_chkBox = tk.Checkbutton(self.window)
        self.TestMode_chkBox["justify"] = "left"
        self.TestMode_chkBox["anchor"] = "w"
        self.TestMode_chkBox["text"] = 'Test'
        self.TestMode_chkBox["variable"] = self.TestMode
        self.TestMode_chkBox["onvalue"] = True
        self.TestMode_chkBox["offvalue"] = False
        self.TestMode_chkBox.place(x=0,y=80,width=60,height = 25)

    #setting test mode txt label and box
        #Lable
        self.test_time_txtLbl=tk.Label(self.window)
        self.test_time_txtLbl['font'] = ft
        self.test_time_txtLbl["fg"] = "#000000"
        self.test_time_txtLbl["justify"] = "center"
        self.test_time_txtLbl["text"] = "Duración (s):"
        self.test_time_txtLbl.place(x=55,y=80,width=80,height=25)
        # txt box
        global test_time_txtBox
        test_time_txtBox=tk.Entry(self.window)
        test_time_txtBox["borderwidth"] = "1px"
        test_time_txtBox["font"] = ft
        test_time_txtBox["fg"] = "#333333"
        test_time_txtBox["justify"] = "center"
        test_time_txtBox["text"] = "test_time"
        test_time_txtBox.place(x=135,y=80,width=40,height=25)

    #setting OSC transmit mode check box
        self.OSC_Transmit = tk.BooleanVar()
        self.OSC_Transmit_chkBox = tk.Checkbutton(self.window)
        self.OSC_Transmit_chkBox["justify"] = "left"
        self.OSC_Transmit_chkBox["anchor"] = "w"
        self.OSC_Transmit_chkBox["text"] = 'Transmitir OSC'
        self.OSC_Transmit_chkBox["variable"] = self.OSC_Transmit
        self.OSC_Transmit_chkBox["onvalue"] = True
        self.OSC_Transmit_chkBox["offvalue"] = False
        self.OSC_Transmit_chkBox.place(x=0,y=120,width=180,height = 25)
        self.OSC_Transmit_chkBox.select()

    #setting close button
        self.button_close_BT = tk.Button(self.window)
        self.button_close_BT["bg"] = "#999999"
        self.button_close_BT["font"] = ft
        self.button_close_BT["fg"] = "#000000"
        self.button_close_BT["justify"] = "center"
        self.button_close_BT["text"] = "Close"
        self.button_close_BT["command"] = self.Close_BT_command
        self.button_close_BT.place(x=0,y=155,width=180,height=30)
   
    def Close_BT_command(self):
        if self.TestMode.get(): 
            self.test_time = int(test_time_txtBox.get())
        self.finished_flag = True
        self.window.destroy()
        
        