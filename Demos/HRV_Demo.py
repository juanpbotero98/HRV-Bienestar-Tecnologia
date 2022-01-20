import biosppy
import pyhrv.tools as tools
from pyhrv.hrv import hrv
from opensignalsreader import OpenSignalsReader
import pyhrv
import pyhrv.frequency_domain as fd
import matplotlib.pyplot as plt
import os 
# Load sample ECG signal stored in an OpenSignals file
file = os.path.join(os.path.abspath(os.getcwd()),'SampleECG.txt')
signal = OpenSignalsReader(file).signal('ECG')
signal_results = hrv(signal=signal)

# Load sample nni series
# nni = [115,131,130,122,131,131,127,130,127,116,114,119,114,115,122,120,124,129,127,130,130,124,125,126,122,117,123,122,120,132,129,123,131,130,130,132,125,126,125,122,120,129,126,117,120,121,118,121,124,120,125,133,119,119,120,122,118,121,124,123,122,126,122,119,122,118,113,120,141,135,133,133,122,117,116,110,100,106,110,107,104,111,113,110,122,127,118,116,115,110,104,107,106,105,105,111,112,109,119,118,113,119,126,124,122,118,106,99,100,121,117,127,136,127,125,127,119,116,117,114,109,107,105,99,105,113,106,103,107,114,107,112,114,100,103,108,113,109,123,131,126,124,120,112,109,110,109,106,114,119,112,114,117,116,113,120,113,108,109,101,104,122,125,123,130,130,127,125,121,118,113,97,96,93,93,95,101,145,132,142,136,132,137,133,132,131,123,116,116,119,106,108,117,119,109,120,139,128,130,132,123,121,123,119,110,122,127,127,138,133,126,130,126,125,128,120,127,125,120,123,127,120,122,124,118,120,133,128,128,125,117,120,122,117,110,113,111,105,109,130,138,132,127,128,129,124,122,118,114,118,120,117,119,126,119,121,125,121,121,122,117,111,111]
nni_results = hrv(nni = nni,plot_ecg=False, plot_tachogram=False, show=False)
print('prueba')
plt.close('all')
tachogram = tools.tachogram(nni = nni)
psd = fd.welch_psd(nni = nni)

# Frequency Comparisson Plots
comparisson_2D = fd.psd_comparison(nni=nni, duration=60, method='welch')
comparisson_3D = fd.psd_waterfall(nni=nni, duration=60, method='welch')

# Time Comparisson Radar Plot
reference_nni = nni[:300]
comparison_nni = nni[300:]
params = ['nni_mean', 'sdnn', 'rmssd', 'nn50', 'nn20']
comparisson_radar = tools.radar_chart(nni = reference_nni, comparison_nni=comparison_nni, parameters=params)
print(nni_results)