import os 
import json
import csv
hrv_reports_path = os.path.join(os.getcwd(),'HRV_Reports')
reports_pathlist = os.listdir(hrv_reports_path)
fnames = ['HRV_baseline.json','HRV_olfative.json','HRV_sound.json','HRV_video.json','HRV_interactive.json','HRV_final.json']

export_path = os.path.join(os.getcwd(),'test.csv')

with open(export_path,mode='w') as export_file:
    writer = csv.writer(export_file)
    header = ["usuario","NN50_baseline","pNN50_baseline","NN20_baseline","pNN20_baseline","rmssd_baseline","sdnn_baseline","LF/HF_baseline-FFT","LF/HF_baseline-AR","LF/HF_baseline-LOMB",
                        "NN50_olfativo","pNN50_olfativo","NN20_olfativo","pNN20_olfativo","rmssd_olfativo","sdnn_olfativo","LF/HF_olfativo-FFT","LF/HF_olfativo-AR","LF/HF_olfativo-LOMB",
                        "NN50_auditivo","pNN50_auditivo","NN20_auditivo","pNN20_auditivo","rmssd_auditivo","sdnn_auditivo","LF/HF_auditivo-FFT","LF/HF_auditivo-AR","LF/HF_auditivo-LOMB",
                        "NN50_visual","pNN50_visual","NN20_visual","pNN20_visual","rmssd_visual","sdnn_visual","LF/HF_visual-FFT","LF/HF_visual-AR","LF/HF_visual-LOMB",
                        "NN50_interactivo","pNN50_interactivo","NN20_interactivo","pNN20_interactivo","rmssd_interactivo","sdnn_interactivo","LF/HF_interactivo-FFT","LF/HF_interactivo-AR","LF/HF_interactivo-LOMB",
                        "NN50_final","pNN50_final","NN20_final","pNN20_final","rmssd_final","sdnn_final","LF/HF_final-FFT","LF/HF_final-AR","LF/HF_final-LOMB"]
    writer.writerow(header)
    for i in range(len(reports_pathlist)):
        row_data = []
        for j in range(len(fnames)):
            path = os.path.join(hrv_reports_path,reports_pathlist[i],fnames[j])
            file = open(path)
            data = json.load(file)

            write_data = [data["nn50"],data["pnn50"],data["nn20"],data["pnn20"],data["rmssd"],data["sdnn"],data["fft_ratio"],data["ar_ratio"],data["lomb_ratio"]]
            # write_data.insert(0,fnames[j][:-5])
            if j == 0:
                write_data.insert(0,i)
            row_data.append(write_data)
        writer.writerow(row_data)

