import biosppy
import pyhrv.tools as tools
from pyhrv.hrv import hrv
from opensignalsreader import OpenSignalsReader

# Load sample ECG signal stored in an OpenSignals file
signal = OpenSignalsReader('SampleECG.txt').signal('ECG')
signal_results = hrv(signal=signal)
# print(signal_results)