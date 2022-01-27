import os 
import json
import csv
from ecgdetectors import Detectors
# import hrv
from pyhrv.hrv import hrv
import pyhrv.tools as tools 
import numpy as np
import biosppy
import matplotlib.pyplot as plt

# detectors = Detectors(130)
# hrv_class = hrv.HRV(130)

hrv_reports_path = os.path.join(os.getcwd(),'HRV_Reports')
reports_pathlist = os.listdir(hrv_reports_path)

fnames = ['ECG_baseline.csv','ECG_olfative.csv','ECG_sound.csv','ECG_video.csv','ECG_interactive.csv','ECG_final.csv']

for path in reports_pathlist:
    export_path = os.path.join(hrv_reports_path,path,'IBI_GeneralData.csv')

    with open(export_path,mode='w') as export_file:
        writer = csv.writer(export_file)
        header_row = ['IBI_baseline','IBI_olfative','IBI_sound','IBI_video','IBI_interactive','IBI_final']
        # writer.writerow(header)

        for ecg_fname in fnames:
            ecg_path = os.path.join(hrv_reports_path,path,ecg_fname)
            # all_ecg = np.
            with open(ecg_path) as ecg_file:
                csv_reader = csv.reader(ecg_file,delimiter = ',')
                line_count = 0 
                for row in csv_reader:
                    if line_count == 0:
                        ECG = row
                        ECG = ECG[1:]
                        ECG = [float(i) for i in ECG]
                        loaded_ecg= biosppy.signals.ecg.ecg(ECG,sampling_rate=130,show = False)
                        plt.close('all') 
                        IBI = []
                        for i in range(len(loaded_ecg[2])-1):
                            IBI.append(loaded_ecg[0][loaded_ecg[2][i+1]]-loaded_ecg[0][loaded_ecg[2][i]])
                        line_count += 1
                        json_fname = 'HRV' + ecg_fname[3:-4]
                        nni_results= hrv(nni=IBI,plot_ecg=False, plot_tachogram=False, show=False)
                        plt.close('all')
                        tools.hrv_export(nni_results,efile=json_fname,path=os.path.join(hrv_reports_path,path,''))

                        IBI.insert(0,ecg_fname)
                        writer.writerow(IBI)
                    else: 
                        line_count += 1