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
from Utils import HRV_Utils, OSC_CommUtils, GUI_Utils, BLE_Utils

####################################################################################################################################
###############   TODO list:                                                                                         ############### 
###############            * Add save raw data function to utils class                                               ###############
###############            * Add BLE scan button                                                                     ###############
###############            * Add BLE connect button                                                                  ###############
####################################################################################################################################

# GUI class
class GUI:
# -------------------- GUI Desing Initialization -----------------------
# ----------- Labels/txt Boxes/Buttons/Variables/Flags -----------------
    def __init__(self, root,loop):        
    # Utility functions and modules 
        self.root = root
        self.loop = loop
        self.osc_utils = OSC_CommUtils
        self.hrv_utils = HRV_Utils
        self.gui_utils = GUI_Utils(self.root)
        self.ble_utils = BLE_Utils

    # Variables 
        self.measurement_status, self.HRV_ratio, self.HeartRate = tk.StringVar() , tk.StringVar(), tk.StringVar()
        self.HF_LF, self.bpm = tk.IntVar(),tk.IntVar()

        self.section_times = [240,240,240,240,240,240]  # [Init , olfative, video, sound, interactive, Final]
        self.section_names = ["Toma de datos previa","Experiecia olfativa",  "Experiencia de sonido", "Experiencia de video","Experiencia interactiva", "Toma de datos final"]
        self.export_path = os.path.join(os.path.abspath(os.getcwd()),"HRV_Reports")

        self.nni_list = [pyhrv.utils.load_sample_nni()]*6 #For testing purpouses
        # TODO: Remove ^ and add self.general_nni = []\
        
        # Container for time session time and data
        self.ecg_session_data = []
        self.ecg_session_time = []
        self.general_ecg = []

    # BLE Variables
        self.selected_MAC = ''
        ## UUID for connection establsihment with device ##
        self.PMD_SERVICE = "FB005C80-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of stream settings ##
        self.PMD_CONTROL = "FB005C81-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of start stream ##
        self.PMD_DATA = "FB005C82-02E7-F387-1CAD-8ACD2D8DF0C8"
        ## UUID for Request of ECG Stream ##
        self.ECG_WRITE = bytearray([0x02, 0x00, 0x00, 0x01, 0x82, 0x00, 0x01, 0x01, 0x0E, 0x00])

        
    # Flags 
        self.baseline_done, self.olfative_done, self.sound_done, self.video_done, self.interactive_done= False, False, False, False, False

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
        self.canvas.create_rectangle(515,335,695,435,fill = '#ededed') # Data Analisis separation
        self.canvas.create_rectangle(515,445,695,555,fill = '#ededed') # Data Analisis separation   
        self.canvas.create_rectangle(515,565,695,635,fill = '#ededed') # Data Analisis separation

        
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
        Status_txtLbl.place(x=520,y=265,width=75,height=25)
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
        self.measurement_pb = Progressbar(self.root, orient='horizontal', length=150, mode='indeterminate',maximum = 35)
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
        # plt.subplots_adjust(left=0.114, bottom=0.186, right=0.97, top=0.94)

        ## Plot configurations
        plt.style.use("ggplot")
        plt.ion()
        self.fig = plt.figure(figsize=(15, 6))
        self.ax = self.fig.add_subplot()
        # self.fig.show()

        plt.title("Live ECG Stream on Polar-H10", fontsize=15, )
        plt.ylabel("Voltage in millivolts", fontsize=15)
        plt.xlabel("Time in (ms)", fontsize=10, )

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
        HeartRate_txtLbl.place(x=520,y=375,width=170,height=25)
        self.HeartRate.set('Frecuencia Cardiaca (bpm): ' + str(self.bpm.get()))
        # HRV Ratio Label
        RatioHRV_txtLbl=tk.Label(root)
        RatioHRV_txtLbl['font'] = ft
        RatioHRV_txtLbl["fg"] = "#000000"
        RatioHRV_txtLbl["justify"] = "left"
        RatioHRV_txtLbl["anchor"] = "w"
        RatioHRV_txtLbl["textvariable"] = self.HRV_ratio
        RatioHRV_txtLbl.place(x=520,y=410,width=170,height=25)
        self.HRV_ratio.set('Ratio HRV (HF/LF): ' + str(self.HF_LF.get()))

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
        DataSave_title.place(x=515,y=445,width=180,height=30)

        #setting export HRV button
        Export_HRV_BT=tk.Button(root)
        Export_HRV_BT["bg"] = "#999999"
        Export_HRV_BT["font"] = ft
        Export_HRV_BT["fg"] = "#000000"
        Export_HRV_BT["justify"] = "center"
        Export_HRV_BT["text"] = "Exportar Analisis HRV"
        Export_HRV_BT["command"] = self.ExportHRV_BT_command
        Export_HRV_BT.place(x=520,y=485,width=170,height=25)
        
        #setting save button
        Save_BT=tk.Button(root)
        Save_BT["bg"] = "#999999"
        Save_BT["font"] = ft
        Save_BT["fg"] = "#000000"
        Save_BT["justify"] = "center"
        Save_BT["text"] = "Guardar ECG"
        Save_BT["command"] = self.Save_BT_command
        Save_BT.place(x=520,y=520,width=170,height=25)

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
        CommSettings_title.place(x=515,y=565,width=180,height=30)
        

        #setting width parameter txt label and box
        #Lable
        IP_txtLbl=tk.Label(root)
        IP_txtLbl['font'] = ft
        IP_txtLbl["fg"] = "#000000"
        IP_txtLbl["justify"] = "center"
        IP_txtLbl["text"] = "Dirección IP:"
        IP_txtLbl.place(x=520,y=602,width=75,height=25)
        #Box
        self.IP_txtBox=tk.Entry(root)
        self.IP_txtBox["borderwidth"] = "1px"
        self.IP_txtBox["font"] = ft
        self.IP_txtBox["fg"] = "#333333"
        self.IP_txtBox["justify"] = "center"
        self.IP_txtBox["text"] = "IP"
        self.IP_txtBox.place(x=610,y=602,width=75,height=25)

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
        BLE_Device_txtLbl.place(x=0,y=610,width=75,height=25)

        #Device dropdown selection list
        device_tkVar = tk.StringVar()
        self.device_list_dropdown = Combobox(root,textvariable=device_tkVar)
        self.device_list_dropdown.place(x=80,y=610,width=150,height=25)

        #setting BLE scan button
        BLE_Scan_BT=tk.Button(root)
        BLE_Scan_BT["bg"] = "#999999"
        BLE_Scan_BT["font"] = ft
        BLE_Scan_BT["fg"] = "#000000"
        BLE_Scan_BT["justify"] = "center"
        BLE_Scan_BT["text"] = "Buscar"
        BLE_Scan_BT["command"] = self.BLE_Scan_BT_command
        BLE_Scan_BT.place(x=315,y=610,width=75,height=25)

        #setting BLE select button
        Device_Select_BT=tk.Button(root)
        Device_Select_BT["bg"] = "#999999"
        Device_Select_BT["font"] = ft
        Device_Select_BT["fg"] = "#000000"
        Device_Select_BT["justify"] = "center"
        Device_Select_BT["text"] = "Seleccionar"
        Device_Select_BT["command"] = self.Device_Select_BT_command
        Device_Select_BT.place(x=235,y=610,width=75,height=25)

# -------------------- Button functions -----------------------

    def Start_BT_command(self):
        print('start')

    def Stop_BT_command(self):
        self.root.quit()                 # stops mainloop
        self.root.destroy()              # this is necessary on Windows to prevent
                                         # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        print('Stop')

    def Init_BT_command(self):
        if not self.baseline_done:
            init_time = time.time()
            self.cue = 0 
            # while time.time()-init_time< 240: 
            #     # TODO: Add polar data acquisition scheme
            #     HR = 80 # Added for testing purpouses 
            #             # HR should be taken from the data acquisition scheme 
            #     self.osc_utils.transmit(0,HR,self.cue)
            
            # self.loop.run_until_complete(self.main_acquisition())
            asyncio.run(self.main_acquisition())
        else: 
            self.gui_utils.error_popup('La medicion de linea de base ya se ha realizado')

    def Final_BT_command(self):
        if not self.baseline_done:
            init_time = time.time()
            self.cue = 0 
            while time.time()-init_time< 240: 
                # TODO: Add polar data acquisition scheme
                HR = 80 # Added for testing purpouses 
                        # HR should be taken from the data acquisition scheme 
                self.osc_utils.transmit(0,HR,self.cue)
        elif self.interactive_done:
            self.gui_utils.error_popup('La experiencia interactiva aún no ha terminado')
        else: 
            self.gui_utils.error_popup('La medicion final ya se realizó')

    def Save_BT_command(self):
        file = FileDialog.asksaveasfile(title="Save Data File", mode="w", defaultextension="nni.txt")
        print('Save')

    def Plot_DataAnalisis_BT_command(self):
        print('Plot data')

    def ExportHRV_BT_command(self):
        try: 
            dir_name = self.Name_txtBox.get()
            exprt_pth = os.path.join(self.export_path,dir_name)
            os.mkdir(exprt_pth)
            fnames = ['HRV_baseline','HRV_olfative','HRV_sound','HRV_video','HRV_interactive','HRV_final']
            for i in range(len(fnames)):
                self.hrv_utils.Export_HRV(fnames[i],os.path.join(exprt_pth,""),self.nni_list[i])
        except:
            self.gui_utils.error_popup('No se ha ingresado el nombre del sujeto o el folder ya existe')

    def BLE_Scan_BT_command(self):
        device_list = asyncio.run(self.ble_utils.scan_devices())
        self.devices_addresses = []
        self.devices_names = []
        for device in device_list:
            self.devices_names.append(device.name)
            self.devices_addresses.append(device.address)
        self.device_list_dropdown['values'] = self.devices_names

    def Device_Select_BT_command(self):
        index = self.devices_names.index(self.device_list_dropdown.get())
        self.selected_MAC = self.devices_addresses[index]
        
# --------------- Helper functions ------------------
    async def main_acquisition(self):
        try:
            async with BleakClient(self.selected_MAC) as client:
                # tasks = [
                #     asyncio.ensure_future(self.perform_measurement(client)),
                # ]

                # await asyncio.gather(*tasks)

                print(f"Connected: {client.is_connected}")

                # model_number = await client.read_gatt_char(self.ble_utils.MODEL_NBR_UUID)
                # print("Model Number: {0}".format("".join(map(chr, model_number))))

                # manufacturer_name = await client.read_gatt_char(self.ble_utils.MANUFACTURER_NAME_UUID)
                # print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

                # battery_level = await client.read_gatt_char(self.ble_utils.BATTERY_LEVEL_UUID)
                # print("Battery Level: {0}%".format(int(battery_level[0])))

                att_read = await client.read_gatt_char(self.PMD_CONTROL)
                print(att_read)

                await client.write_gatt_char(self.PMD_CONTROL, self.ECG_WRITE)

                ## ECG stream started
                await client.start_notify(self.PMD_DATA, self.data_conv)
                print("Collecting ECG data...")
                n = 130
                init_time = time.time()
                started_flag = False
                while time.time()-init_time<40:
                    print(time.time()-init_time)
                    ## Collecting ECG data for 1 second
                    await asyncio.sleep(1)
                    # print(len(ecg_session_data),len(ecg_session_time))

                    if len(self.ecg_session_data)>0 :
                        if not started_flag:
                            init_time = time.time()
                            started_flag =True
                            print('entered if')
                    
                    if len(self.ecg_session_data)>0 & started_flag:
                        plt.autoscale(enable=True, axis="y", tight=True)
                        self.ax.plot(self.ecg_session_data,color="r")
                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()
                        self.ax.set_xlim(left=n - 130, right=n)
                        n = n + 130
                # await client.stop_notify(self.ble_utils.PMD_DATA)
        except: 
            self.gui_utils.error_popup('No fue posible establecer conexión con el dispositivo')

    async def perform_measurement(self,client):
        # await client.is_connected()
        # print("---------Device connected--------------")

        print(f"Connected: {client.is_connected}")

        # model_number = await client.read_gatt_char(self.ble_utils.MODEL_NBR_UUID)
        # print("Model Number: {0}".format("".join(map(chr, model_number))))

        # manufacturer_name = await client.read_gatt_char(self.ble_utils.MANUFACTURER_NAME_UUID)
        # print("Manufacturer Name: {0}".format("".join(map(chr, manufacturer_name))))

        # battery_level = await client.read_gatt_char(self.ble_utils.BATTERY_LEVEL_UUID)
        # print("Battery Level: {0}%".format(int(battery_level[0])))

        att_read = await client.read_gatt_char(self.ble_utils.PMD_CONTROL)
        print(att_read)

        await client.write_gatt_char(self.ble_utils.PMD_CONTROL, self.ble_utils.ECG_WRITE)

        ## ECG stream started
        await client.start_notify(self.ble_utils.PMD_DATA, self.ble_utils.data_conv)
        n = self.ble_utils.ECG_SAMPLING_FREQ
        init_time = time.time()
        started_flag = False
        while time.time()-init_time<40:
            print(time.time()-init_time)
            ## Collecting ECG data for 1 second
            await asyncio.sleep(1)
            # print(len(ecg_session_data),len(ecg_session_time))

            if len(self.ble_utils.ecg_session_data)>0 :
                if not started_flag:
                    init_time = time.time()
                    started_flag =True
                    print('entered if')
            
            if len(self.ble_utils.ecg_session_data)>0 & started_flag:
                plt.autoscale(enable=True, axis="y", tight=True)
                self.ax.plot(self.ble_utils.ecg_session_data,color="r")
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                self.ax.set_xlim(left=n - 130, right=n)
                n = n + 130
        await client.stop_notify(self.ble_utils.PMD_DATA)

    # Bit conversion of the Hexadecimal stream
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
# ------------------ Main Code ----------------------
if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    root = tk.Tk()
    loop = asyncio.get_event_loop()
    gui = GUI(root,loop)
    root.mainloop()