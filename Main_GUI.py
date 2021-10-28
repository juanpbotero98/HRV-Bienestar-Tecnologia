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
from time import sleep,time
from statistics import mean, pstdev, mode
import numpy as np
from collections import defaultdict
from operator import itemgetter
import os 
import pyhrv
from Utils import HRV_Utils, OSC_CommUtils, GUI_Utils

####################################################################################################################################
###############   TODO list:                                                                                         ############### 
###############            * Add save raw data function to utils class                                               ###############
####################################################################################################################################

# GUI class
class GUI:
# -------------------- GUI Desing Initialization -----------------------
# ----------- Labels/txt Boxes/Buttons/Variables/Flags -----------------
    def __init__(self, root):        
    # Utility functions and modules 
        self.root = root
        self.osc_utils = OSC_CommUtils
        self.hrv_utils = HRV_Utils
        self.gui_utils = GUI_Utils(self.root)

    # Variables 
        self.measurement_status, self.HRV_ratio, self.HeartRate = tk.StringVar() , tk.StringVar(), tk.StringVar()
        self.HF_LF, self.bpm = tk.IntVar(),tk.IntVar()

        self.section_times = [240,240,240,240,240,240]  # [Init , olfative, video, sound, interactive, Final]
        self.section_names = ["Toma de datos previa","Experiecia olfativa",  "Experiencia de sonido", "Experiencia de video","Experiencia interactiva", "Toma de datos final"]
        self.export_path = os.path.join(os.path.abspath(os.getcwd()),"HRV_Reports")

        self.nni_list = [pyhrv.utils.load_sample_nni()]*6 #For testing purpouses
        # TODO: Remove ^ and add self.general_nni = []

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

    # Communication Settings Panel 
        #setting parameter title label
        CommSettings_title=tk.Label(root)
        CommSettings_title["bg"] = "#000000"
        ft = tkFont.Font(family='Times',size=10)
        CommSettings_title["font"] = ft
        CommSettings_title["fg"] = "#fbfbfb"
        CommSettings_title["justify"] = "center"
        CommSettings_title["text"] = "Ajustes OSC"
        CommSettings_title["relief"] = "raised"
        CommSettings_title.place(x=515,y=150,width=180,height=30)
        

        #setting width parameter txt label and box
        #Lable
        IP_txtLbl=tk.Label(root)
        IP_txtLbl['font'] = ft
        IP_txtLbl["fg"] = "#000000"
        IP_txtLbl["justify"] = "center"
        IP_txtLbl["text"] = "Dirección IP:"
        IP_txtLbl.place(x=520,y=190,width=75,height=25)
        #Box
        self.IP_txtBox=tk.Entry(root)
        self.IP_txtBox["borderwidth"] = "1px"
        self.IP_txtBox["font"] = ft
        self.IP_txtBox["fg"] = "#333333"
        self.IP_txtBox["justify"] = "center"
        self.IP_txtBox["text"] = "IP"
        self.IP_txtBox.place(x=610,y=190,width=75,height=25)

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
        self.figure,self.ax = plt.subplots()
        # plt.axis('off')
        plt.subplots_adjust(left=0.114, bottom=0.186, right=0.97, top=0.94)
        plot_canvas = FigureCanvasTkAgg(self.figure, master=root)
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
        Subjects_Name_title.place(x=515,y=565,width=180,height=30)

        # setting subjects name txt box
        self.Name_txtBox=tk.Entry(root)
        self.Name_txtBox["borderwidth"] = "1px"
        self.Name_txtBox["font"] = ft
        self.Name_txtBox["fg"] = "#333333"
        self.Name_txtBox["justify"] = "center"
        self.Name_txtBox["text"] = "Name"
        self.Name_txtBox.place(x=520,y=602,width=170,height=25)

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
            while time.time()-init_time< 240: 
                # TODO: Add polar data acquisition scheme
                HR = 80 # Added for testing purpouses 
                        # HR should be taken from the data acquisition scheme 
                self.osc_utils.transmit(0,HR,self.cue)
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
            self.gui_utils.error_popup('La experiencia interactiva aun no ha terminado')
        else: 
            self.gui_utils.error_popup('La medicion final ya se ha realizado')

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

# -------------------- Helper functions -----------------------

# -------------------- Main Code --------------------
if __name__ == "__main__":
    root = tk.Tk()
    gui = GUI(root)
    root.mainloop()