from pycbc.waveform import get_td_waveform
from pycbc.filter import match
from pycbc.psd import aLIGOZeroDetHighPower
import matplotlib.pyplot as plt
import numpy as np

f_low = 30
sample_rate = 4096

template_mass = [10,20,30,40,50]
tmass = [10,20,30,40,50]
m=[]
for i in template_mass:
    for j in range(len(template_mass)):

    
    # Generate the two waveforms to compare
        hp, hc = get_td_waveform(approximant="EOBNRv2",
                                 mass1=30,
                                 mass2=30,
                                 f_lower=f_low,
                                 delta_t=1.0/sample_rate)

        sp, sc = get_td_waveform(approximant="TaylorT4",
                                 mass1=i,
                                 mass2=tmass[j],
                                 f_lower=f_low,
                                 delta_t=1.0/sample_rate)

    # Resize the waveforms to the same length
        tlen = max(len(sp), len(hp))
        sp.resize(tlen)
        hp.resize(tlen)

    # Generate the aLIGO ZDHP PSD
        delta_f = 1.0 / sp.duration
        flen = tlen//2 + 1
        psd = aLIGOZeroDetHighPower(flen, delta_f, f_low)

    # Note: This takes a while the first time as an FFT plan is generated
    # subsequent calls are much faster.
        m_point, i = match(hp, sp, psd=psd, low_frequency_cutoff=f_low)
    
        m.append(m_point)
print(m)
