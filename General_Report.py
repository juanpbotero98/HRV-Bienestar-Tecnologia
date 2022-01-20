import os 
import json
import csv
hrv_reports_path = os.path.join(os.getcwd(),'HRV_Reports')
reports_pathlist = os.listdir(hrv_reports_path)
fnames = ['HRV_baseline.json','HRV_olfative.json','HRV_sound.json','HRV_video.json','HRV_interactive.json','HRV_final.json']

export_path = os.path.join(os.getcwd(),'test.csv')

with open(export_path,mode='w') as export_file:
    writer = csv.writer(export_file)
    header = ["usuario","estimulo","ar_ratio","fft_ratio","lomb_ratio","rmssd","sdnn"]
    writer.writerow(header)
    for i in range(len(reports_pathlist)):
        for j in range(len(fnames)):
            path = os.path.join(hrv_reports_path,reports_pathlist[i],fnames[j])
            file = open(path)
            data = json.load(file)

            write_data = [data["ar_ratio"],data["fft_ratio"],data["lomb_ratio"],data["rmssd"],data["sdnn"]]
            write_data.insert(0,fnames[j][:-5])
            write_data.insert(0,i)
            writer.writerow(write_data)

