#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 11:53:59 2021

@author: urjashah
"""

#TOPIC - GRAV WAVE DETECTORS 

#SUB -detector locations
from pycbc.detector import Detector, get_available_detectors
for abv, long_name in get_available_detectors():
    d = Detector(abv)

    # Note that units are all in radians
    print("{} {} Latitude {} Longitude {}".format(long_name, abv,
                                                  d.latitude,
                                                  d.longitude))
#SUB -light travel time between detectors 
from pycbc.detector import Detector

for ifo1 in ['H1', 'L1', 'V1']: #what is ifo1?
    for ifo2 in ['H1', 'L1', 'V1']:
        dt = Detector(ifo1).light_travel_time_to_detector(Detector(ifo2))
        print("Direct Time from {} to {} is {} seconds".format(ifo1, ifo2, dt))
        
#SUB - time soure gravitational wave passes through detector
from pycbc.detector import Detector
from astropy.utils import iers

# Make sure the documentation can be built without an internet connection
iers.conf.auto_download = False

# The source of the gravitational waves
right_ascension = 0.7
declination = -0.5

# Reference location will be the Hanford detector
# see the `time_delay_from_earth_center` method to use use geocentric time
# as the reference
dref = Detector("H1")

# Time in GPS seconds that the GW passes
time = 100000000

# Time that the GW will (or has) passed through the given detector
for ifo in ["H1", "L1", "V1"]:
    d = Detector(ifo)
    dt = d.time_delay_from_detector(dref, right_ascension, declination, time)
    st = "GW passed through {} {} seconds relative to passing by Hanford"
    print(st.format(ifo, dt))

#SUB - antenna patterns and projecting a signal into the detector frame
from pycbc.detector import Detector
from pycbc.waveform import get_td_waveform

# Time, orientation and location of the source in the sky
ra = 1.7
dec = 1.7
pol = 0.2 #??
inc = 0
time = 1000000000

# We can calcualate the antenna pattern for Hanford at
# the specific sky location
d = Detector("H1")

# We get back the fp and fc antenna pattern weights.
fp, fc = d.antenna_pattern(ra, dec, pol, time)
print("fp={}, fc={}".format(fp, fc))

# These factors allow us to project a signal into what the detector would
# observe

## Generate a waveform
hp, hc = get_td_waveform(approximant="IMRPhenomD", mass1=10, mass2=10,
                         f_lower=30, delta_t=1.0/4096, inclination=inc,
                         distance=400)

## Apply the factors to get the detector frame strain
ht = fp * hp + fc * hc #what are these?


# The projection process can also take into account the rotation of the
# earth using the project wave function.
hp.start_time = hc.start_time = time

#TOPIC - WAVEFORMS

#SUB - what waveforms can be generated?
from pycbc.waveform import td_approximants, fd_approximants

# List of td approximants that are available
print(td_approximants())

# List of fd approximants that are currently available
print(fd_approximants())

#SUB- Plotting TD waveforms
import pylab
from pycbc.waveform import get_td_waveform

for apx in ['SEOBNRv2', 'IMRPhenomC']:
    hp, hc = get_td_waveform(approximant=apx,
                                 mass1=10,
                                 mass2=10,
                                 spin1z=0.9,
                                 delta_t=1.0/4096,
                                 f_lower=40)

    pylab.plot(hp.sample_times, hp, label=apx)

pylab.ylabel('Strain')
pylab.xlabel('Time (s)')
pylab.legend()
pylab.show()

#SUB - Generating one waveform in multiple detectors
import pylab
from pycbc.waveform import get_td_waveform
from pycbc.detector import Detector

apx = 'SEOBNRv4'
# NOTE: Inclination runs from 0 to pi, with poles at 0 and pi
#       coa_phase runs from 0 to 2 pi.
hp, hc = get_td_waveform(approximant=apx,
                         mass1=10,
                         mass2=10,
                         spin1z=0.9,
                         spin2z=0.4,
                         inclination=1.23,
                         coa_phase=2.45,
                         delta_t=1.0/4096,
                         f_lower=40)

det_h1 = Detector('H1')
det_l1 = Detector('L1')
det_v1 = Detector('V1')

# Choose a GPS end time, sky location, and polarization phase for the merger
# NOTE: Right ascension and polarization phase runs from 0 to 2pi
#       Declination runs from pi/2. to -pi/2 with the poles at pi/2. and -pi/2.
end_time = 1192529720
declination = 0.65
right_ascension = 4.67
polarization = 2.34
hp.start_time += end_time
hc.start_time += end_time

signal_h1 = det_h1.project_wave(hp, hc,  right_ascension, declination, polarization)
signal_l1 = det_l1.project_wave(hp, hc,  right_ascension, declination, polarization)
signal_v1 = det_v1.project_wave(hp, hc,  right_ascension, declination, polarization)

pylab.plot(signal_h1.sample_times, signal_h1, label='H1')
pylab.plot(signal_l1.sample_times, signal_l1, label='L1')
pylab.plot(signal_v1.sample_times, signal_v1, label='V1')

pylab.ylabel('Strain')
pylab.xlabel('Time (s)')
pylab.legend()
pylab.show()

#SUB - Calculating the match between waveforms
from pycbc.waveform import get_td_waveform
from pycbc.filter import match
from pycbc.psd import aLIGOZeroDetHighPower

f_low = 30
sample_rate = 4096

# Generate the two waveforms to compare
hp, hc = get_td_waveform(approximant="EOBNRv2",
                         mass1=10,
                         mass2=10,
                         f_lower=f_low,
                         delta_t=1.0/sample_rate)

sp, sc = get_td_waveform(approximant="TaylorT4",
                         mass1=10,
                         mass2=10,
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
m, i = match(hp, sp, psd=psd, low_frequency_cutoff=f_low)
print('The match is: {:.4f}'.format(m))

#SUB - plotting td and fd together in the td

# Plot a time domain and fourier domain waveform together in the time domain.
# Note that without special cleanup the Fourier domain waveform will exhibit
# the Gibb's phenomenon. (http://en.wikipedia.org/wiki/Gibbs_phenomenon)

import pylab
from pycbc import types, fft, waveform

# Get a time domain waveform
hp, hc = waveform.get_td_waveform(approximant="EOBNRv2",
                             mass1=6, mass2=6, delta_t=1.0/4096, f_lower=40)

# Get a frequency domain waveform
sptilde, sctilde = waveform. get_fd_waveform(approximant="TaylorF2",
                             mass1=6, mass2=6, delta_f=1.0/4, f_lower=40)

# FFT it to the time-domain
tlen = int(1.0 / hp.delta_t / sptilde.delta_f)
sptilde.resize(tlen/2 + 1)
sp = types.TimeSeries(types.zeros(tlen), delta_t=hp.delta_t)
fft.ifft(sptilde, sp)

pylab.plot(sp.sample_times, sp, label="TaylorF2 (IFFT)")
pylab.plot(hp.sample_times, hp, label="EOBNRv2")

pylab.ylabel('Strain')
pylab.xlabel('Time (s)')
pylab.legend()
pylab.show()

#SUB - Plotting GW phases and amplitude of the td waveform
import pylab
from pycbc import waveform

for apx in ['EOBNRv2', 'TaylorT4', 'IMRPhenomB']:
    hp, hc = waveform.get_td_waveform(approximant=apx,
                                 mass1=10,
                                 mass2=10,
                                 delta_t=1.0/4096,
                                 f_lower=40)

    hp, hc = hp.trim_zeros(), hc.trim_zeros()
    amp = waveform.utils.amplitude_from_polarizations(hp, hc)
    phase = waveform.utils.phase_from_polarizations(hp, hc)

    pylab.plot(phase, amp, label=apx)

pylab.ylabel('GW Strain Amplitude')
pylab.xlabel('GW Phase (radians)')
pylab.legend(loc='upper left')
pylab.show()

#SUB - plotting frequency evolution of td waveform
import pylab
from pycbc import waveform

for phase_order in [2, 3, 4, 5, 6, 7]:
    hp, hc = waveform.get_td_waveform(approximant='SpinTaylorT4',
                                 mass1=10, mass2=10,
                                 phase_order=phase_order,
                                 delta_t=1.0/4096,
                                 f_lower=100)

    hp, hc = hp.trim_zeros(), hc.trim_zeros()
    amp = waveform.utils.amplitude_from_polarizations(hp, hc)
    f = waveform.utils.frequency_from_polarizations(hp, hc)

    pylab.plot(f.sample_times, f, label="PN Order = %s" % phase_order)

pylab.ylabel('Frequency (Hz)')
pylab.xlabel('Time (s)')
pylab.legend(loc='upper left')
pylab.show()