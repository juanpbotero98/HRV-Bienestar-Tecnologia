import os 
import json
import csv
from ecgdetectors import Detectors
import hrv

detectors = Detectors(130)
hrv_class = hrv.HRV(130)
hrv_reports_path = os.path.join(os.getcwd(),'HRV_Reports')
reports_pathlist = os.listdir(hrv_reports_path)

fnames = ['ECG_baseline.csv','ECG_olfative.csv','ECG_sound.csv','ECG_video.csv','ECG_interactive.csv','ECG_final.csv']
export_path = os.path.join(os.getcwd(),'hrv_report_V2.csv')

with open(export_path,mode='w') as export_file:
    writer = csv.writer(export_file)
    header = ["usuario","NN50_baseline","pNN50_baseline","NN20_baseline","pNN20_baseline","rmssd_baseline","sdnn_baseline","LF/HF_baseline",
                        "NN50_olfativo","pNN50_olfativo","NN20_olfativo","pNN20_olfativo","rmssd_olfativo","sdnn_olfativo","LF/HF_olfativo",
                        "NN50_auditivo","pNN50_auditivo","NN20_auditivo","pNN20_auditivo","rmssd_auditivo","sdnn_auditivo","LF/HF_auditivo",
                        "NN50_visual","pNN50_visual","NN20_visual","pNN20_visual","rmssd_visual","sdnn_visual","LF/HF_visual",
                        "NN50_interactivo","pNN50_interactivo","NN20_interactivo","pNN20_interactivo","rmssd_interactivo","sdnn_interactivo","LF/HF_interactivo",
                        "NN50_final","pNN50_final","NN20_final","pNN20_final","rmssd_final","sdnn_final","LF/HF_final"]
    writer.writerow(header)
    for i in range(len(reports_pathlist)):
        participant_row = []
        for j in range(len(fnames)):
            csv_path = os.path.join(hrv_reports_path,reports_pathlist[i],fnames[j])
            with open(csv_path) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        ECG = row
                        ECG = ECG[1:]
                        ECG = [float(i) for i in ECG]
                        r_peaks = detectors.wqrs_detector(ECG)
                        NN50 = hrv_class.NN50(r_peaks)
                        pNN50 = hrv_class.pNN50(r_peaks)
                        NN20 = hrv_class.NN20(r_peaks)
                        pNN20 = hrv_class.pNN20(r_peaks)
                        RMSSD = hrv_class.RMSSD(r_peaks)
                        SDNN = hrv_class.SDNN(r_peaks)
                        fAnalysis = hrv_class.fAnalysis(r_peaks)
                        participant_row.append(NN50)
                        participant_row.append(pNN50)
                        participant_row.append(NN20)
                        participant_row.append(pNN20)
                        participant_row.append(RMSSD)
                        participant_row.append(SDNN)
                        participant_row.append(fAnalysis)
                        line_count += 1
                        
                    else:
                        line_count += 1
        participant_row.insert(0,i)
        writer.writerow(participant_row)
        print(i)