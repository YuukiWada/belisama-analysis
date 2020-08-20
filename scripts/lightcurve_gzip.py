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
if len(args)<4:
    print("Error: invalid number of arguments")
    print("Usage: python lightcurve_gzip.py <input file> <bin width (sec)> <lower threshold (ch)> <upper threshold (ch)>")
    exit()

input_file=args[1]
bin_width=float(args[2])
lower=int(args[3])
upper=int(args[4])

data=np.loadtxt(input_file, delimiter=",").transpose()
unixtime=np.array(data[0])
phamax=np.array(data[1])
duration=unixtime[len(unixtime)-1]-unixtime[0]
bin_num=math.floor(duration/bin_width)+1
bin_max=float(bin_num)*bin_width

time_data=data_selection(data, upper, lower)
start_time=time_data[0][0]
second=time_data[0]-start_time
weights=np.ones(len(second))/bin_width

# plot data
plt.hist(second, range=(0.0, bin_max), bins=bin_num, histtype="step", weights=weights, color="black")
plt.xlabel("time (sec)")
plt.ylabel("count rate (counts/s)")
plt.xlim(0.0, bin_max)
plt.show()
