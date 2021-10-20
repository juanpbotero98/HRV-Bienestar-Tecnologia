import biosppy
import pyhrv.tools as tools
from pyhrv.hrv import hrv
from opensignalsreader import OpenSignalsReader
import pyhrv
import pyhrv.frequency_domain as fd

# Load sample ECG signal stored in an OpenSignals file
# signal = OpenSignalsReader('SampleECG.txt').signal('ECG')
# signal_results = hrv(signal=signal)

# Load sample nni series
nni = pyhrv.utils.load_sample_nni()
# nni_results = hrv(nni = nni)
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