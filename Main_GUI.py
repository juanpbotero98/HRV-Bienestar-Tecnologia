import tkinter as tk
import tkinter.font as tkFont
from tkinter import filedialog as FileDialog
from tkinter.ttk import Progressbar,Combobox
import sys
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib.animation as animation
from time import sleep
import time
from statistics import mean, pstdev, mode
import numpy as np
from collections import defaultdict
from operator import itemgetter
import os 
import pyhrv
import asyncio
from bleak import BleakClient
from Utils import HRV_Utils, OSC_CommUtils, GUI_Utils, BLE_Utils, OperationModes_Popup
from bleak.uuids import uuid16_dict
from PIL import Image, ImageTk
from tkinter import *
import random

####################################################################################################################################
###############   TODO list:                                                                                         ############### 
###############            * Add save raw data function to utils class                                               ###############
###############   BUG list:                                                                                          ###############
###############            * Support for various mesurements is failing                                              ###############
####################################################################################################################################

# GUI class
class GUI:
# -------------------- GUI Desing Initialization -----------------------
# ----------- Labels/txt Boxes/Buttons/Variables/Flags -----------------
    def __init__(self, root,loop):        
    # Utility functions and modules
        self.root = root
        self.loop = loop
        # self.osc_utils = OSC_CommUtils(ip="157.253.138.93")
        self.hrv_utils = HRV_Utils
        self.gui_utils = GUI_Utils(self.root)
        self.ble_utils = BLE_Utils
        self.opmodes_popup = OperationModes_Popup(self.root)

    # Variables
        self.measurement_status, self.HRV_ratio, self.HeartRate, self.battery_percentage = tk.StringVar() , tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.HF_LF, self.bpm = tk.IntVar(),tk.IntVar()

        self.section_time = 240 
        self.section_names = ["Experiecia olfativa",  "Experiencia de sonido", "Experiencia de video","Experiencia interactiva"]
        self.current_path = os.path.abspath(os.getcwd())
        self.export_path = os.path.join(self.current_path,"HRV_Reports")
        self.image_path = os.path.join(self.current_path,"Icons")

        self.nni_list = [pyhrv.utils.load_sample_nni()]*6 #For testing purpouses
        # TODO: Remove ^ and add self.general_nni = []\
       
        # Data containers
        self.ecg_session_data = []
        self.ecg_session_time = []
        self.general_ecg = [[],[],[],[],[],[]] # Data container for ECG data [Init , olfative, sound, video, interactive, Final]
        self.general_hr = [[],[],[],[],[],[]] # Data container for HR data [Init , olfative, sound, video, interactive, Final]
        self.general_ibi = [[],[],[],[],[],[]] # Data container for IBI data [Init , olfative, sound, video, interactive, Final]
        self.cue = 1
        self.HR_data = {}
        self.HR_data["rr"] = []
        self.HR_data["hr"] = []

        # Biofeedback Color Pallet
        self.feedback_color = [3877,3098,3085,3076,3069,3064,2336,915]

    # Button Icon Images
        settings_icon_realsize = PhotoImage(file = os.path.join(self.image_path,'Settings_Icon.png'))
        self.settings_icon = settings_icon_realsize.subsample(3,3)

    # BLE Variables
        # MAC Addres of the device to connect
        self.selected_MAC = ''
        ## UUID for connection establsihment with device ##
        self.PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of stream settings ##
        self.PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of start stream ##
        self.PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of ECG Stream ##
        self.ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])
        ## UUID Dictonary
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
        ## UUID for Request HR data 
        self.HR_UUID = "00002A37-0000-1000-8000-00805F9B34FB"
 
    # Flags
        self.baseline_done, self.experience_done, self.final_done= False, False, False # Experience stage 
        self.hrv_exported, self.ecg_saved = False, False # Saving succes 
        self.OPmodes_popup,self.testmode, self.ctrl_group = False, False,False # OP Modes
        self.OSC_transmit = True # Transmitir OSC
        self.OSC_connected = False # Conectado a servidor OSC

    # Canvas operations
        #setting main tittle
        root.title("Bienestar & Tecnología")
        #setting window size
        window_width=700
        window_height=640
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (window_width, window_height, (screenwidth - window_width) / 2,
                                    (screenheight - window_height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)    
        #setting separation lines
        self.canvas = tk.Canvas(root)
        # self.canvas.create_line(0,400,400,400,dash=(4,2))
        self.canvas.create_line(505,0,505,window_height,dash=(4,2))
       
        #setting separation rectangles
        self.canvas.create_rectangle(515,30,695,140,fill = '#ededed') # Control panel separation
        self.canvas.create_rectangle(515,150,695,225,fill = '#ededed') # Communication Settings separation
        self.canvas.create_rectangle(515,235,695,325,fill = '#ededed') # Status panel separation
        self.canvas.create_rectangle(515,335,695,390,fill = '#ededed') # Data Analisis separation
        self.canvas.create_rectangle(515,400,695,510,fill = '#ededed') # Data Analisis separation  
        self.canvas.create_rectangle(515,520,695,625,fill = '#ededed') # Data Analisis separation

       
        self.canvas.pack(fill= 'both', expand=1)
        #setting font
        self.ft = tkFont.Font(family='Times',size=10)

    # Measurement Control Panel
        #setting  title label
        Controls_title=tk.Label(root)
        Controls_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        Controls_title["font"] = ft
        Controls_title["fg"] = "#fbfbfb"
        Controls_title["justify"] = "center"
        Controls_title["text"] = "Funciones de Control"
        Controls_title["relief"] = "raised"
        Controls_title.place(x=515,y=0,width=180,height=30)
       
        #setting start button
        Start_BT=tk.Button(root)
        Start_BT["bg"] = "#30cc00"
        Start_BT["font"] = ft
        Start_BT["fg"] = "#000000"
        Start_BT["justify"] = "center"
        Start_BT["text"] = "Start"
        Start_BT["command"] = self.Start_BT_command
        Start_BT.place(x=520,y=40,width=75,height=40)
       
        #setting stop button
        Stop_BT=tk.Button(root)
        Stop_BT["bg"] = "#cc0000"
        Stop_BT["font"] = ft
        Stop_BT["fg"] = "#000000"
        Stop_BT["justify"] = "center"
        Stop_BT["text"] = "Stop"
        Stop_BT["command"] = self.Stop_BT_command
        Stop_BT.place(x=615,y=40,width=75,height=40)

        #setting initial measurement button
        Init_BT=tk.Button(root)
        Init_BT["bg"] = "#999999"
        Init_BT["font"] = ft
        Init_BT["fg"] = "#000000"
        Init_BT["justify"] = "center"
        Init_BT["text"] = "Init"
        Init_BT["command"] = self.Init_BT_command
        Init_BT.place(x=520,y=90,width=75,height=40)
       
        #setting stop button
        Final_BT=tk.Button(root)
        Final_BT["bg"] = "#999999"
        Final_BT["font"] = ft
        Final_BT["fg"] = "#000000"
        Final_BT["justify"] = "center"
        Final_BT["text"] = "Final"
        Final_BT["command"] = self.Final_BT_command
        Final_BT.place(x=615,y=90,width=75,height=40)

    #  Subjects Identification Panel
        #setting Statistics Panel title label
        Subjects_Name_title=tk.Label(root)
        Subjects_Name_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        Subjects_Name_title["font"] = ft
        Subjects_Name_title["fg"] = "#fbfbfb"
        Subjects_Name_title["justify"] = "center"
        Subjects_Name_title["text"] = "Nombre del Sujeto"
        Subjects_Name_title["relief"] = "raised"
        Subjects_Name_title.place(x=515,y=150,width=180,height=30)

        # setting subjects name txt box
        self.Name_txtBox=tk.Entry(root)
        self.Name_txtBox["borderwidth"] = "1px"
        self.Name_txtBox["font"] = ft
        self.Name_txtBox["fg"] = "#333333"
        self.Name_txtBox["justify"] = "center"
        self.Name_txtBox["text"] = "Name"
        self.Name_txtBox.place(x=520,y=190,width=170,height=25)

    # Status Panel
        #setting LED Control Panel title label
        Status_title=tk.Label(root)
        Status_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        Status_title["font"] = ft
        Status_title["fg"] = "#fbfbfb"
        Status_title["justify"] = "center"
        Status_title["text"] = "Progreso de la Medición"
        Status_title["relief"] = "raised"
        Status_title.place(x=515,y=235,width=180,height=30)

        #setting status txt label
        Status_txtLbl=tk.Label(root)
        Status_txtLbl['font'] = ft
        Status_txtLbl["fg"] = "#000000"
        Status_txtLbl["justify"] = "left"
        Status_txtLbl["anchor"] = "w"
        Status_txtLbl["textvariable"] = self.measurement_status
        Status_txtLbl.place(x=520,y=265,width=170,height=25)
        self.measurement_status.set('Estado: ')

        #Setting progress widget
        #Label
        self.MeasurementPB_txtLbl=tk.Label(root)
        self.MeasurementPB_txtLbl['font'] = ft
        self.MeasurementPB_txtLbl["fg"] = "#000000"
        self.MeasurementPB_txtLbl["justify"] = "left"
        self.MeasurementPB_txtLbl["anchor"] = "w"
        self.MeasurementPB_txtLbl["text"] = "Progreso:"
        self.MeasurementPB_txtLbl.place(x=520,y=300,width=75,height=25)
        #Widget
        self.measurement_pb = Progressbar(self.root, orient='horizontal', length=100, mode='indeterminate',maximum = 35)
        #Done message
        self.done_mssg=tk.Label(root)
        self.done_mssg['font'] = ft
        self.done_mssg["fg"] = "#30cc00"
        self.done_mssg["justify"] = "right"
        self.done_mssg["text"] = "Terminado"

    #  Data Display
        #setting Data Plot title label
        Plot_title=tk.Label(root)
        Plot_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        Plot_title["font"] = ft
        Plot_title["fg"] = "#fbfbfb"
        Plot_title["justify"] = "center"
        Plot_title["text"] = "ECG Data"
        Plot_title["relief"] = "raised"
        Plot_title.place(x=0,y=0,width=500,height=30)
       
        # plt.ion()
        # self.figure,self.ax = plt.subplots()
        # plt.axis('off')
       

        ## Plot configurations
        plt.style.use("ggplot")
        # plt.ion()
        self.fig = plt.figure(figsize=(15, 6))
        self.ax = self.fig.add_subplot()
        plt.subplots_adjust(left=0.11, bottom=0.143, right=0.964, top=0.976)
        # self.fig.show()

        # plt.title("Live ECG Stream on Polar-H10", fontsize=15, )
        plt.ylabel("Voltaje [mV]", fontsize=10)
        plt.xlabel("Tiempo [ms]", fontsize=10, )

        plot_canvas = FigureCanvasTkAgg(self.fig, master=root)
        plot_canvas.get_tk_widget().place(x=0,y=30,width = 500 , height = 535)

        toolbar = NavigationToolbar2Tk(plot_canvas, root)
        toolbar.place(x=0,y=535,width=500,height=30)
        toolbar.update()
   
    #  Data Analisis
        #setting Statistics Panel title label
        DataAnalisis_title=tk.Label(root)
        DataAnalisis_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        DataAnalisis_title["font"] = ft
        DataAnalisis_title["fg"] = "#fbfbfb"
        DataAnalisis_title["justify"] = "center"
        DataAnalisis_title["text"] = "Datos Cardiacos"
        DataAnalisis_title["relief"] = "raised"
        DataAnalisis_title.place(x=515,y=335,width=180,height=30)

        #setting variable labels for data statistics
        # HR Label
        HeartRate_txtLbl=tk.Label(root)
        HeartRate_txtLbl['font'] = ft
        HeartRate_txtLbl["fg"] = "#000000"
        HeartRate_txtLbl["justify"] = "left"
        HeartRate_txtLbl["anchor"] = "w"
        HeartRate_txtLbl["textvariable"] = self.HeartRate
        HeartRate_txtLbl.place(x=520,y=365,width=170,height=25)
        self.HeartRate.set('Frecuencia Cardiaca (bpm): ' + str(self.bpm.get()))
        
        # HRV Ratio Label
        # RatioHRV_txtLbl=tk.Label(root)
        # RatioHRV_txtLbl['font'] = ft
        # RatioHRV_txtLbl["fg"] = "#000000"
        # RatioHRV_txtLbl["justify"] = "left"
        # RatioHRV_txtLbl["anchor"] = "w"
        # RatioHRV_txtLbl["textvariable"] = self.HRV_ratio
        # RatioHRV_txtLbl.place(x=520,y=410,width=170,height=25)
        # self.HRV_ratio.set('Ratio HRV (HF/LF): ' + str(self.HF_LF.get()))

    #  Data Save Panel  
        #setting Statistics Panel title label
        DataSave_title=tk.Label(root)
        DataSave_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        DataSave_title["font"] = ft
        DataSave_title["fg"] = "#fbfbfb"
        DataSave_title["justify"] = "center"
        DataSave_title["text"] = "Funciones de guardado"
        DataSave_title["relief"] = "raised"
        DataSave_title.place(x=515,y=400,width=180,height=30)

        #setting export HRV button
        Export_HRV_BT=tk.Button(root)
        Export_HRV_BT["bg"] = "#999999"
        Export_HRV_BT["font"] = ft
        Export_HRV_BT["fg"] = "#000000"
        Export_HRV_BT["justify"] = "center"
        Export_HRV_BT["text"] = "Guardar Datos"
        Export_HRV_BT["command"] = self.ExportHRV_BT_command
        Export_HRV_BT.place(x=520,y=440,width=170,height=25)
       
        #setting save button
        Save_BT=tk.Button(root)
        Save_BT["bg"] = "#999999"
        Save_BT["font"] = ft
        Save_BT["fg"] = "#000000"
        Save_BT["justify"] = "center"
        Save_BT["text"] = "SIN USO (TEMPORAL)"
        Save_BT["command"] = self.Save_BT_command
        Save_BT.place(x=520,y=475,width=170,height=25)

    # OSC Settings Panel
        #setting parameter title label
        CommSettings_title=tk.Label(root)
        CommSettings_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        CommSettings_title["font"] = ft
        CommSettings_title["fg"] = "#fbfbfb"
        CommSettings_title["justify"] = "center"
        CommSettings_title["text"] = "Ajustes OSC"
        CommSettings_title["relief"] = "raised"
        CommSettings_title.place(x=515,y=520,width=180,height=30)
       

        #setting IP parameter txt label and box
        #Lable
        IP_txtLbl=tk.Label(root)
        IP_txtLbl['font'] = ft
        IP_txtLbl["fg"] = "#000000"
        IP_txtLbl["justify"] = "center"
        IP_txtLbl["text"] = "Dirección IP:"
        IP_txtLbl.place(x=520,y=560,width=75,height=25)
        #Box
        self.IP_txtBox=tk.Entry(root)
        self.IP_txtBox["borderwidth"] = "1px"
        self.IP_txtBox["font"] = ft
        self.IP_txtBox["fg"] = "#333333"
        self.IP_txtBox["justify"] = "center"
        self.IP_txtBox["text"] = "IP"
        self.IP_txtBox.place(x=610,y=560, width=75,height=25)
        self.IP_txtBox.insert(0,"157.253.26.191")
       
        #OSC Connect Button
        OSC_Connect_BT = tk.Button(root)
        OSC_Connect_BT["bg"] = "#999999"
        OSC_Connect_BT["font"] = ft
        OSC_Connect_BT["fg"] = "#000000"
        OSC_Connect_BT["justify"] = "center"
        OSC_Connect_BT["text"] = "Conectar OSC"
        OSC_Connect_BT["command"] = self.OSC_Connect_BT_command
        OSC_Connect_BT.place(x=520,y=595,width=170,height=25)

    # Operation mode Popup button    
        Mode_Popup_BT = tk.Button(root)
        Mode_Popup_BT = tk.Button(root)
        Mode_Popup_BT["bg"] = "#999999"
        Mode_Popup_BT["font"] = ft
        Mode_Popup_BT["fg"] = "#000000"
        Mode_Popup_BT["justify"] = "center"
        Mode_Popup_BT["text"] = "..."
        Mode_Popup_BT["image"] = self.settings_icon
        Mode_Popup_BT["command"] = self.Mode_Popup_BT_command
        Mode_Popup_BT.place(x=665,y=625,width=25,height=18)

    # BLE Settings Panel
        #setting BLE Settings title label
        BLE_Settings_title=tk.Label(root)
        BLE_Settings_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        BLE_Settings_title["font"] = ft
        BLE_Settings_title["fg"] = "#fbfbfb"
        BLE_Settings_title["justify"] = "center"
        BLE_Settings_title["text"] = "Polar Bluetooth Settings"
        BLE_Settings_title["relief"] = "raised"
        BLE_Settings_title.place(x=0,y=570,width=500,height=30)

        #BLE Device Label
        BLE_Device_txtLbl=tk.Label(root)
        BLE_Device_txtLbl['font'] = ft
        BLE_Device_txtLbl["fg"] = "#000000"
        BLE_Device_txtLbl["justify"] = "center"
        BLE_Device_txtLbl["anchor"] = "w"
        BLE_Device_txtLbl["text"] = "Dispositivo:"
        BLE_Device_txtLbl.place(x=0,y=610,width=70,height=25)

        #Device dropdown selection list
        device_tkVar = tk.StringVar()
        self.device_list_dropdown = Combobox(root,textvariable=device_tkVar)
        self.device_list_dropdown.place(x=75,y=610,width=150,height=25)

        #setting BLE scan button
        BLE_Scan_BT=tk.Button(root)
        BLE_Scan_BT["bg"] = "#999999"
        BLE_Scan_BT["font"] = ft
        BLE_Scan_BT["fg"] = "#000000"
        BLE_Scan_BT["justify"] = "center"
        BLE_Scan_BT["text"] = "Buscar"
        BLE_Scan_BT["command"] = self.BLE_Scan_BT_command
        BLE_Scan_BT.place(x=310,y=610,width=75,height=25)

        #setting BLE select button
        Device_Select_BT=tk.Button(root)
        Device_Select_BT["bg"] = "#999999"
        Device_Select_BT["font"] = ft
        Device_Select_BT["fg"] = "#000000"
        Device_Select_BT["justify"] = "center"
        Device_Select_BT["text"] = "Seleccionar"
        Device_Select_BT["command"] = self.Device_Select_BT_command
        Device_Select_BT.place(x=230,y=610,width=75,height=25)

        #Baterry Label
        self.Battery_txtLbl=tk.Label(root)
        self.Battery_txtLbl['font'] = ft
        self.Battery_txtLbl["fg"] = "#000000"
        self.Battery_txtLbl["justify"] = "center"
        self.Battery_txtLbl["text"] = "Batería:"

        #Battery percentage label
        self.Battery_Percentage_txtLbl=tk.Label(root)
        self.Battery_Percentage_txtLbl['font'] = ft
        self.Battery_Percentage_txtLbl["justify"] = "center"
        self.Battery_Percentage_txtLbl["anchor"] = "w"
        self.Battery_Percentage_txtLbl["textvariable"] =  self.battery_percentage

# -------------------- Button functions -----------------------

    def Start_BT_command(self):
        self.verify_flags()
        if self.OSC_transmit and not self.OSC_connected:
            self.gui_utils.error_popup("No está conectado a OSC")

        elif self.baseline_done:
            print('start')

            # Randomize the color pallet of the biofeedback
            if self.OSC_transmit:
                self.osc_utils.custom_transmit("COLOR",random.choice(self.feedback_color))
                self.osc_utils.custom_transmit("/Audio",1)

            self.start_status = 1
            asyncio.run(self.main_acquisition(loop = 4,transmit=self.OSC_transmit,section_time=self.section_time))
            self.experience_done = True
                     
            if len(self.general_ecg[1]) == 0:
                self.experience_done = False

            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 15:
                    self.osc_utils.transmit(1,80,5,0)
        
        elif self.ctrl_group:
            print('started control group measurement')
            asyncio.run(self.ctrlGroup_acquisition(section_time=self.section_time))
            self.experience_done = True
            self.final_done = True

        elif self.testmode:
            print('running test without baseline')
            
            # Randomize the color pallet of the biofeedback
            if self.OSC_transmit:
                print('Heart color sent')
                final_time = time.time()
                self.osc_utils.custom_transmit("/COLOR",random.choice(self.feedback_color))
                self.osc_utils.custom_transmit("/Audio",0)
            
            self.start_status = 0
            asyncio.run(self.main_acquisition(loop = 4,transmit=self.OSC_transmit,section_time=self.section_time))
            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 15:
                    self.osc_utils.transmit(1,80,5,0)
            self.restart_vars() 
            # TODO Verify function
            
        else:
            self.gui_utils.error_popup('No se ha realizado la medición baseline')

    def Stop_BT_command(self):
        
        if self.ctrl_group: 
            self.restart_vars()

        self.root.quit()                 # stops mainloop
        self.root.destroy()              # this is necessary on Windows to prevent
                                         # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        print('Stop')

    def Init_BT_command(self):
        self.verify_flags()
        # if self.ctrl_group:
        #     self.gui_utils.error_popup('Error: Está en modo grupo control')
        if not self.baseline_done:
            self.cue = 0 # Cue variable that controls the experience flow
            self.start_status = 0 # Start variable that controls the experience start/stop
            self.measurement_status.set('Estado:        Baseline')
            asyncio.run(self.main_acquisition(loop = 1,transmit = False,section_time=self.section_time))
            self.done_mssg.place(x=600,y=300,width=75,height=25)
            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 15:
                    self.osc_utils.transmit(0,0,0,0)

        elif self.baseline_done and self.final_done:
            print("Empezó una nueva medición y se reiniciaron las variables")
            self.restart_vars()
            self.cue = 0 # Cue variable that controls the experience flow
            self.start_status = 0 # Start variable that controls the experience start/stop
            self.measurement_status.set('Estado:        Baseline')
            asyncio.run(self.main_acquisition(loop = 1, transmit = False,section_time=self.section_time))
            self.done_mssg.place(x=600,y=300,width=75,height=25) 
            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 15:
                    self.osc_utils.transmit(0,0,0,0)   
        else:
            self.gui_utils.error_popup('La medicion de linea de base ya se ha realizado')

    def Final_BT_command(self):
        if self.experience_done and (not self.final_done):
            self.cue = 0
            self.start_status = 0
            self.measurement_status.set('Estado:        Final')
            asyncio.run(self.main_acquisition(loop = 1, transmit = False,section_time=self.section_time))
            self.final_done = True
            
            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 15:
                    self.osc_utils.transmit(0,0,0,0)
            print(len(self.general_ecg[0][0]))
            print(len(self.general_ecg[1][0]))
            print(len(self.general_ecg[2][0]))
            print(len(self.general_ecg[3][0]))
            print(len(self.general_ecg[4][0]))
            # Restart cues
            final_time = time.time()
            if self.OSC_transmit:
                while time.time() - final_time < 30:
                    self.osc_utils.transmit(0,0,0,0)
            
        elif self.final_done:
            self.gui_utils.error_popup('La medicion final ya se realizó, si no intente de nuevo')
            self.final_done = False
        else:
            self.gui_utils.error_popup('La experiencia interactiva aún no ha terminado')

    def Save_BT_command(self):
        # self.hrv_utils.Save_ECG(self.general_ecg,self.final_done,self.full_export_path)
        # self.ecg_saved = True
        # self.gui_utils.error_popup('Botón sin funcionalidad...')
        if self.OSC_connected:
            self.osc_utils.custom_transmit("/Audio",1)
        else:
            self.gui_utils.error_popup('No está conectado a OSC')

    def ExportHRV_BT_command(self):
        try:
            # Export path changes depending on operation mode 
            if self.ctrl_group:
                temp_export_path = os.path.join(self.export_path,"Grupo_Control")
                fnames = ['Momento_1','Momento_2','Momento_3','Momento_4','Momento_5','Momento_6']
            else: 
                temp_export_path = os.path.join(self.export_path,"Experiencia_Mindfullness")
                fnames = ['HRV_baseline','HRV_olfative','HRV_sound','HRV_video','HRV_interactive','HRV_final']
            
            # Manage directories and create output folder
            dir_name = self.Name_txtBox.get()
            self.full_export_path = os.path.join(temp_export_path,dir_name)
            os.mkdir(self.full_export_path)
            
            # Save raw ECG data
            self.hrv_utils.Save_ECG(self.general_ecg,self.final_done,self.full_export_path,self.general_hr,self.general_ibi)
            self.ecg_saved = True
            print('ECG Saved')

            # Analyze ECG data and export HRV reports
            for i in range(len(fnames)):
                self.hrv_utils.Export_HRV(fnames[i],os.path.join(self.full_export_path,""),self.general_ecg[i][0])
            self.hrv_exported = True
            print('HRV Saved')
            
        except:
            self.gui_utils.error_popup('No se ha ingresado el nombre del sujeto o el folder ya existe')
            print(sys.exc_info()[0])

    def BLE_Scan_BT_command(self):
        device_list = asyncio.run(self.ble_utils.scan_devices())
        self.devices_addresses = []
        self.devices_names = []
        for device in device_list:
            self.devices_names.append(device.name)
            self.devices_addresses.append(device.address)
        self.device_list_dropdown['values'] = self.devices_names
    
    def Device_Select_BT_command(self):
        # Establish MAC Address and get device battery level
        index = self.devices_names.index(self.device_list_dropdown.get())
        self.selected_MAC = self.devices_addresses[index]
        self.battery_level = asyncio.run(self.get_battery())
        # Place Baterry level indicator
        self.Battery_txtLbl.place(x=400,y=610,width=50,height=25)
        if self.battery_level is None:
            pass
        elif self.battery_level >= 60:
            self.Battery_Percentage_txtLbl['fg'] = "#30cc00"
        elif self.battery_level <= 20:
            self.Battery_Percentage_txtLbl['fg'] = "#cc0000"
        else:
            self.Battery_Percentage_txtLbl['fg'] = "orange"
        self.battery_percentage.set("{0}%".format(self.battery_level))
        self.Battery_Percentage_txtLbl.place(x=455,y=610,width=50,height=25)
       
    def OSC_Connect_BT_command(self):
        self.osc_utils = OSC_CommUtils(ip=self.IP_txtBox.get())
        print(" OSC connected to ip: {0}".format(self.IP_txtBox.get()))
        self.OSC_connected = True

    def Mode_Popup_BT_command(self):
        self.OPmodes_popup = True
        self.opmodes_popup.popup()
        
        
# --------------- Helper functions ------------------
    # Acquisition Loop
    async def main_acquisition(self,loop,transmit,section_time):
        try:
            async with BleakClient(self.selected_MAC) as client:
                print(f"Connected: {client.is_connected}")

                # battery_level = await client.read_gatt_char(self.ble_utils.BATTERY_LEVEL_UUID)
                # print("Battery Level: {0}%".format(int(battery_level[0])))

                att_read = await client.read_gatt_char(self.PMD_CONTROL)
                print(att_read)
                time.sleep(1)
                await client.write_gatt_char(self.PMD_CONTROL, self.ECG_WRITE)

                ## ECG stream started
                await client.start_notify(self.PMD_DATA, self.data_conv)
                await client.start_notify(self.HR_UUID, self.data_conv_hr)
                print("Collecting ECG & HR data...")

                # Managing progress bar and labels
                if self.baseline_done or self.experience_done:
                    # Destroy the done label and re-define the progressbar widget and labels
                    self.done_mssg.destroy()
                    #Widget
                    self.measurement_pb = Progressbar(self.root, orient='horizontal', length=100, mode='indeterminate',maximum = 35)
                    #Done message
                    self.done_mssg=tk.Label(self.root)
                    self.done_mssg['font'] = self.ft
                    self.done_mssg["fg"] = "#30cc00"
                    self.done_mssg["justify"] = "right"
                    self.done_mssg["text"] = "Terminado"
                self.measurement_pb.start(interval = 1) #Start the progress bar
                self.measurement_pb.place(x=590,y=300)

                # Main acquisition loop
                for i in range(loop):
                    n = 130
                    started_flag = False
                    self.ecg_session_data = []
                    self.ecg_session_time = []
                    if loop > 1:
                        self.measurement_status.set('Estado:    {}'.format(self.section_names[i]))
                    init_time = time.time()
                    while time.time()-init_time<section_time:
                        print(time.time()-init_time)
                        ## Collecting ECG data for 1 second
                        await asyncio.sleep(1)
                        # print(len(ecg_session_data),len(ecg_session_time))

                        if len(self.ecg_session_data)>0:
                            if not started_flag:
                                self.HR_data["hr"] = []
                                self.HR_data["rr"] = []
                                init_time = time.time()
                                started_flag =True
                                # print('entered if')
                        
                        if started_flag:
                            # Update figure
                            plt.autoscale(enable=True, axis="y", tight=True)
                            self.ax.plot(self.ecg_session_data,color="r")
                            self.fig.canvas.draw()
                            self.fig.canvas.flush_events()
                            self.ax.set_xlim(left=n - 130, right=n)
                            n = n + 130
                            # Update txt label
                        
                            if transmit:
                                if len(self.HR_data["rr"]) > 0:
                                    self.osc_utils.transmit(self.start_status,self.bpm.get(),self.cue,self.HR_data["rr"][-1])
                                    self.bpm.set(self.HR_data["hr"][-1])
                                    self.HeartRate.set('Frecuencia Cardiaca (bpm): ' + str(self.bpm.get()))
                        

                            

                    if not self.baseline_done:
                        print("Saved data baseline in variable")
                        self.general_ecg[i] = [self.ecg_session_data,self.ecg_session_time]
                        self.general_hr[i] =  self.HR_data["hr"]
                        self.general_ibi[i] = self.HR_data["rr"] 
                        self.baseline_done = True

                    elif not self.experience_done:
                        print("saved data experience {} in variable".format(i))
                        self.general_ecg[i+1] = [self.ecg_session_data,self.ecg_session_time]
                        self.general_hr[i+1] =  self.HR_data["hr"]
                        self.general_ibi[i+1] = self.HR_data["rr"] 
                    
                    else: 
                        print("Saved data final in variable")
                        self.general_ecg[-1] = [self.ecg_session_data,self.ecg_session_time]
                        self.general_hr[i] =  self.HR_data["hr"]
                        self.general_ibi[i] = self.HR_data["rr"] 
                        
                    
                    # Debugging 
                    # print(len(self.ecg_session_data))
                    if len(self.ecg_session_data)>0:
                        self.cue += 1
                        # Restart figure
                        self.ax.cla()
                # Stop progressbar
                self.measurement_pb.stop()
                self.measurement_pb.destroy()
                # Set done label
                self.done_mssg.place(x=600,y=300,width=75,height=25)
                # await client.stop_notify(self.ble_utils.PMD_DATA)
        except: 
            self.gui_utils.error_popup('No fue posible establecer conexión con el dispositivo')

    # Control Group Acquisition Loop
    async def ctrlGroup_acquisition(self,section_time):
        try:
            async with BleakClient(self.selected_MAC) as client:
                print(f"Connected: {client.is_connected}")

                # att_read = await client.read_gatt_char(self.PMD_CONTROL)
                # print(att_read)

                # Measurements Quality Check
                # await client.start_notify(self.PMD_CONTROL, self.data_print) 
                # WRITE = bytearray([0x01, 0x00])
                # await client.write_gatt_char(self.PMD_CONTROL, WRITE,response=True)
                # Start Measurement
                time.sleep(1) 
                await client.write_gatt_char(self.PMD_CONTROL, self.ECG_WRITE)
                # await client.stop_notify(self.PMD_DATA)

                ## ECG stream started
                await client.start_notify(self.PMD_DATA, self.data_conv)
                print("Collecting ECG data...")

                if  self.experience_done:
                    # Destroy the done label and re-define the progressbar widget and labels
                    self.done_mssg.destroy()
                    #Widget
                    self.measurement_pb = Progressbar(self.root, orient='horizontal', length=100, mode='indeterminate',maximum = 35)
                    #Done message
                    self.done_mssg=tk.Label(self.root)
                    self.done_mssg['font'] = self.ft
                    self.done_mssg["fg"] = "#30cc00"
                    self.done_mssg["justify"] = "right"
                    self.done_mssg["text"] = "Terminado"

                self.measurement_pb.start(interval = 1) #Start the progress bar
                self.measurement_pb.place(x=590,y=300)
                # Main acquisition loop
                for i in range(6):
                    n = 130
                    started_flag = False
                    self.ecg_session_data = []
                    self.ecg_session_time = []
                    self.measurement_status.set('Estado:    {} out of 6'.format(i+1))
                    init_time = time.time()
                    while time.time()-init_time<section_time:
                        print(time.time()-init_time)
                        ## Collecting ECG data for 1 second
                        await asyncio.sleep(1)
                        # print(len(self.ecg_session_data))

                        if len(self.ecg_session_data)>0:
                            if not started_flag:
                                init_time = time.time()
                                started_flag =True
                                # print('entered if')
                        
                        # print(started_flag)
                        if started_flag:
                            plt.autoscale(enable=True, axis="y", tight=True)
                            self.ax.plot(self.ecg_session_data,color="r")
                            self.fig.canvas.draw()
                            self.fig.canvas.flush_events()
                            self.ax.set_xlim(left=n - 130, right=n)
                            n = n + 130
                    self.general_ecg[i] = [self.ecg_session_data,self.ecg_session_time]
                    print('saved ecg {}/6 in variable'.format(i+1))
                    # Restart figure
                    self.ax.cla()
                # Stop progressbar
                self.measurement_pb.stop()
                self.measurement_pb.destroy()
                # Set done label
                self.done_mssg.place(x=600,y=300,width=75,height=25)
                await client.stop_notify(self.PMD_DATA)

        except: 
            self.gui_utils.error_popup('No fue posible establecer conexión con el dispositivo')

    # def data_print(self,sender, data):
    #     print(', '.join('{:02x}'.format(x) for x in data))

    # Byte conversion of the Hexadecimal stream
    def data_conv(self, sender, data):
        if data[0] == 0x00:
            timestamp = self.convert_to_unsigned_long(data, 1, 8)
            step = 3
            samples = data[10:]
            offset = 0
            while offset < len(samples):
                ecg = self.convert_array_to_signed_int(samples, offset, step)
                offset += step
                self.ecg_session_data.extend([ecg])
                self.ecg_session_time.extend([timestamp])

    def convert_array_to_signed_int(self,data, offset, length):
        return int.from_bytes(
            bytearray(data[offset : offset + length]), byteorder="little", signed=True,
        )

    def convert_to_unsigned_long(self,data, offset, length):
        return int.from_bytes(
            bytearray(data[offset : offset + length]), byteorder="little", signed=False,
        )

    def data_conv_hr(self,sender,data):
        """
        data is a list of integers corresponding to readings from the BLE HR monitor
        """

        byte0 = data[0]
        self.HR_data["hrv_uint8"] = (byte0 & 1) == 0
        sensor_contact = (byte0 >> 1) & 3
        if sensor_contact == 2:
            self.HR_data["sensor_contact"] = "No contact detected"
        elif sensor_contact == 3:
            self.HR_data["sensor_contact"] = "Contact detected"
        else:
            self.HR_data["sensor_contact"] = "Sensor contact not supported"
        self.HR_data["ee_status"] = ((byte0 >> 3) & 1) == 1
        self.HR_data["rr_interval"] = ((byte0 >> 4) & 1) == 1

        if self.HR_data["hrv_uint8"]:
            self.HR_data["hr"].append(data[1])
            i = 2
        else:
            self.HR_data["hr"].append((data[2] << 8) | data[1])
            i = 3

        if self.HR_data["ee_status"]:
            self.HR_data["ee"] = (data[i + 1] << 8) | data[i]
            i += 2

        if self.HR_data["rr_interval"]:
            while i < len(data):
                # Note: Need to divide the value by 1024 to get in seconds
                self.HR_data["rr"].append((data[i + 1] << 8) | data[i])
                i += 2
    
    # Get device battery
    async def get_battery(self):
        try:
            async with BleakClient(self.selected_MAC) as client:
                print(f"Connected: {client.is_connected}")
                battery_level = await client.read_gatt_char(self.BATTERY_LEVEL_UUID)
                print("Battery Level: {0}%".format(int(battery_level[0])))
                return int(battery_level[0])
        
        except:
            self.gui_utils.error_popup('No fue posible establecer conexión con el dispositivo')

    # Restart variables
    def restart_vars(self):
        if self.ecg_saved or self.hrv_exported:
            # Restart ecg data container
            self.general_ecg = [[],[],[],[],[],[]]
            # Restart flags
            self.baseline_done, self.experience_done, self.final_done= False, False, False # Experience stages
            self.hrv_exported, self.ecg_saved = False, False
            # Destroy the done label and re-define the progressbar widget and labels
            self.done_mssg.destroy()
            #Widget
            self.measurement_pb = Progressbar(self.root, orient='horizontal', length=100, mode='indeterminate',maximum = 35)
            #Done message
            self.done_mssg=tk.Label(self.root)
            self.done_mssg['font'] = self.ft
            self.done_mssg["fg"] = "#30cc00"
            self.done_mssg["justify"] = "right"
            self.done_mssg["text"] = "Terminado"
        else:
            self.gui_utils.error_popup('Guarde primero la medición anterior antes de iniciar una nueva')

    # Op Modes flag handler
    def verify_flags(self):
        if self.OPmodes_popup:
            if self.opmodes_popup.finished_flag:
                self.testmode = self.opmodes_popup.TestMode.get()
                self.ctrl_group = self.opmodes_popup.ControlGroup.get()
                self.OSC_transmit = self.opmodes_popup.OSC_Transmit.get()

            if self.testmode:
                self.section_time = self.opmodes_popup.test_time
                print("Test mode selected")
            
            if self.ctrl_group:
                print("Control group mode selected")

            if not self.OSC_transmit:
                print("OSC communication OFF")
            
# ------------------ Main Code ----------------------
if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    root = tk.Tk()
    loop = asyncio.get_event_loop()
    gui = GUI(root,loop)
    root.mainloop()