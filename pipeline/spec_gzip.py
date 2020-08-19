#!/usr/bin/env python
import matplotlib.pyplot as plt
import numpy as np
import math
import sys


# reading argiment parameters
args=sys.argv
if len(args)<1:
    print("Error: invalid number of arguments")
    print("Usage: python spec_gzip.py <input file> <binning (option)>")
    exit()

input_file=args[1]

if len(args)>2:
    rebin=int(args[2])
    if (rebin>2048) or (rebin<1):
        print("The number of binning should be more than 0 and less than 2048")
        rebin=1
    elif math.log2(rebin).is_integer()!=True:
        print("The number of binning should be 2 to the power of n")
        rebin=1
else:
    rebin=1
bin_num=int(2048/rebin)

data=np.loadtxt(input_file, delimiter=",").transpose()
unixtime=np.array(data[0])
phamax=np.array(data[1])
duration=unixtime[len(unixtime)-1]-unixtime[0]
weights=np.ones(len(phamax))/(float(rebin)*duration)
plt.hist(phamax, range=(-0.5, 2047.5), bins=bin_num, histtype="step", weights=weights)
plt.yscale('log')
plt.xlabel("Channel")
plt.ylabel("Spectrum (counts/ch/s)")
plt.show()
