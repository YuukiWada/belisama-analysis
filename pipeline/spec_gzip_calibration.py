#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import random
import math
import sys


# reading argiment parameters
args=sys.argv
if len(args)<4:
    print("Error: invalid number of arguments")
    print("Usage: python spec_gzip.py <input file> <p0> <p1> <binning (option)>")
    print("Calibration function: Energy (MeV) = p0 + Channel * p1")
    exit()

input_file=args[1]
par=[float(args[2]), float(args[3])]

if len(args)>4:
    rebin=int(args[4])
    if (rebin>2048) or (rebin<1):
        print("The number of binning should be more than 0 and less than 2048")
        rebin=1
    elif math.log2(rebin).is_integer()!=True:
        print("The number of binning should be 2 to the power of n")
        rebin=1
else:
    rebin=1

bin_num=int(1024/rebin)
bin_max=20.0
bin_width=bin_max/float(bin_num)

data=np.loadtxt(input_file, delimiter=",").transpose()
unixtime=np.array(data[0])
phamax=np.array(data[1])
random=np.random.rand(len(phamax))
phamax=par[0]+(phamax+random-0.5)*par[1]
duration=unixtime[len(unixtime)-1]-unixtime[0]
weights=np.ones(len(phamax))/(bin_width*duration)
plt.hist(phamax, range=(0.0, bin_max), bins=bin_num, histtype="step", weights=weights)
plt.yscale('log')
plt.xlabel("Energy (MeV)")
plt.ylabel("Spectrum (counts/s/MeV)")
plt.show()
