#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 13:43:00 2021

@author: urjashah
"""

from pycbc.waveform import get_td_waveform
from pycbc.filter import match
from pycbc.psd import aLIGOZeroDetHighPower
import matplotlib.pyplot as plt
import numpy as np

f_low = 15
sample_rate = 4096

template_mass = [15,20,25]
tmass = [15,20,25]
m=np.zeros([len(template_mass),len(tmass)])
hp, hc = get_td_waveform(approximant="TaylorT2",
                         mass1=20,
                         mass2=20,
                         f_lower=f_low,
                         delta_t=1.0/sample_rate)
for i in template_mass:
    for j in range(len(tmass)):

        sp, sc = get_td_waveform(approximant="TaylorT2",
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
        m_point, k = match(hp, sp, psd=psd, low_frequency_cutoff=f_low)
    
        m[i][j]=m_point
'''  
m_array = np.reshape(m,[5,5])
print(m_array)
    
h = plt.hist2d(m,template_mass)
cbar = plt.colorbar(h[3])
cbar.set_label('probability')
plt.ylabel('mass')
plt.xlabel('match')
plt.show()
'''