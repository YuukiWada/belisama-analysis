#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import math
import sys


def data_selection(data, upper, lower):
    trans=data.transpose()
    selected=(trans[((trans[:,1]>=lower) & (trans[:,1]<upper))]).transpose()
    return selected

# reading argiment parameters
args=sys.argv
if len(args)<6:
    print("Error: invalid number of arguments")
    print("Usage: python lightcurve_gzip.py <input file> <bin width (sec)> <p0> <p1> <lower threshold (MeV)> <upper threshold (MeV)>")
    print("Calibration function: Energy (MeV) = p0 + Channel * p1")
    exit()

input_file=args[1]
bin_width=float(args[2])
par=[float(args[3]), float(args[4])]
lower=float(args[5])
upper=float(args[6])


data=np.loadtxt(input_file, delimiter=",").transpose()
unixtime=np.array(data[0])
phamax=np.array(data[1])
random=np.random.rand(len(phamax))
phamax=par[0]+(phamax+random-0.5)*par[1]
duration=unixtime[len(unixtime)-1]-unixtime[0]
bin_num=math.floor(duration/bin_width)+1
bin_max=float(bin_num)*bin_width

calibrated=np.array([unixtime, phamax])
time_data=data_selection(calibrated, upper, lower)
start_time=time_data[0][0]
second=time_data[0]-start_time
weights=np.ones(len(second))/bin_width

# plot data
plt.hist(second, range=(0.0, bin_max), bins=bin_num, histtype="step", weights=weights, color="black")
plt.xlabel("time (sec)")
plt.ylabel("count rate (counts/s)")
plt.xlim(0.0, bin_max)
plt.show()
