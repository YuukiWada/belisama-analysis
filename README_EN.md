# Belisama Analysis
Analysis framework for Belisama in Python

- Version: 1.0
- Last update: 20 August 2020
- Author: Yuuki Wada

## Introduction
Belisama is a project of radiation measurements during thunderstorms in France. This project is led by Université de Paris/APC, Université d'Orléans/LPC2E, Université de Bourgogne, IRSN, CEA/IRFU, CNES, CNRS/IN2P3, Labex UnivEarth, CSNSM, Société d'Astronomie de Bourgogne, Université de Nagoya, et RIKEN. [The project wesite is here.](https://ikhone.wixsite.com/belisama)

The instrument of radiation measurements provides a list of detected gamma-ray photons: timing and its energy in the form of FITS (flexible image transport system), which is often used for astronomy, astrophysics, earth and space sciences. This analysis frame work is to perform timing calibration and to convert FITS files to CSV files.

### Github
[https://github.com/YuukiWada/belisama-analysis](https://github.com/YuukiWada/belisama-analysis)

### Supported Platform
- Mac OS X
- Linux
- (it should works on Windows machines in which Python is installed.)

### Test environment
- MacBook Air (Retina, 13-inch, 2018)
- macOS Mojave (Version 10.14.4)
- Python 3.7.7
 - astropy 4.0.1.post1
 - matplotlib 3.2.2
 - numpy 1.19.0

## Installation
### Required softwares
- Python (version 3.x is required)
 - astropy
 - matplotlib
 - numpy


 Libraries can be installed by the commands:
 ```
 python -m pip install astropy
 python -m pip install matplotlib
 python -m pip install numpy
 ```

### Clone scripts to local
```
git clone https://github.com/YuukiWada/belisama-analysis.git
```

## Usage
### Pipeline scripts
There are two scripts for pipeline processes:
```
pipeline/fits2csv.py
pipeline/fits2csv_batch.py
```

fits2csv.py converts a FITS file to a CSV file. Its usage is
```
python fits2csv.py <input FITS file> <output directory>
```

fits2csv.py interprets the input FITS file, and dump its data to the indicated output directory. When the commands
```
python fits2csv.py 20200820_140005.fits.gz ./csv
```
is executed,
```
./csv/20200820_140005_ch0.csv.gz
./csv/20200820_140005_ch1.csv.gz
./csv/20200820_140005_ch2.csv.gz
./csv/20200820_140005_ch3.csv.gz
```
will be created. Since the instrument has four input channels, data of each input channel is saved separately. If an input channel has no data, no CSV file of the channel will be created. As a default, the output CSV file is gzip-compressed. Use `zless` to glance at the compressed files.

The output CSV file contains lines
```
1511517035.266076,56,0
1511517035.335293,1196,0
1511517035.391294,120,0
1511517035.458569,49,0
...
```
Each line corresponds to a photon event detected by the instrument. The first column contains the detection time in the unit of UNIXTIME. If GPS signals are properly received by the instruments, the timing accuracy is better than 1 us. If GPS signals are lost, the script trys to calibrate timing with PC time of the instrument. In that case, the timing accuracy is +/- 1 sec when PC time is well adjusted by NTP. If PC time is not well adjusted and GPS signals are lost, the timing accuracy is not reliable.

The second column contains the energy of photon events in the channel unit. This value varies from 0 to 2048. Energy calibration is needed to obtain energy of each photon in the unit of MeV. The most popular way for energy calibration is to use calibration sources: 0.662 MeV of 137Cs. It is also convenient to detect the 1.46-MeV line from 40K and 2.61-MeV from 208Tl. Both 40K and 208Tl are natural isotopes and these lines can be detected as natural environmental background. When the 1.46-MeV line is at 140 channel and the 2.61-MeV line at 247, the calibration function
```
Energy (MeV) = a + b * channel
a=1.46-140.0*b
b=(2.61-1.46)/(247.0-140.0)
```
can be obtained.

The third column contains dead counts: the number of photons that were triggered by the instrument between the last photon record (in the previous line) but not recorded due to buffer overflow. In a normal operation, dead counts are 0. However, dead counts will increase when a lot of photons are
detected instantaneously and photon data cannot be transported from FPGA to Raspberry Pi, or Raspberry Pi has a lot of other background processes that occupy CPU resources.

`fits2csv_batch.py` converts multiple FITS files to CSV files. Its usage is
```
python fits2csv_batch.py <input directory> <output directory>
```

When the commands
```
python fits2csv.py ./fits ./csv
```
is executed, the script trys to find `*.fits` and `*.fits.gz` files in `./fits`, and all the FITS files in the directory are converted into CSV format. The other function is the same as `fits2csv.py`.

### Analysis scripts
There are six scripts for analysis:
```
scripts/spec_fits.py
scripts/spec_gzip.py
scripts/spec_gzip_calibration.py
scripts/lightcurve_fits.py
scripts/lightcurve_gzip.py
scripts/lightcurve_gzip_calibration.py
```

`spec_fits.py` generates an energy spectrum in the channel unit. The usage is
```
python spec_fits.py <input file> <adc channel> <binning (option)>
```
This script is useful to quicklook an energy spectrum of a FITS file before converting into CSV. The input ADC channel should be specified. When binnning is indicated, the energy spectrum will be binned.

`spec_gzip.py` generates an energy spectrum in the channel unit from a converted CSV file. The usage is
```
python spec_gzip.py <input file> <binning (option)>
```

`spec_gzip_calibration.py` generates an energy spectrum in the unit MeV from a converted CSV file. The usage is
```
python spec_gzip.py <input file> <p0> <p1> <binning (option)>
```
p0 and p1 are parameters of a calibration curve given by
```
Energy (MeV) = p0 + Channel * p1"
```
The example of calibration curve is described above.

`lightcurve_fits.py` generates a lightcurve or a count-rate history. The usage is
```
python lightcurve_fits.py <input file> <adc channel> <bin width (sec)> <lower threshold> <upper threshold>
```
This script is useful to quicklook a lightcurve of a FITS file before converting into CSV. The input ADC channel should be specified. Thresholds should be given in the channel unit.

`lightcurve_gzip.py` generates a lightcurve or a count-rate history from a converted CSV file. The usage is
```
python lightcurve_gzip.py <input file> <bin width (sec)> <lower threshold> <upper threshold>
```
Thresholds should be given in the channel unit.

`lightcurve_gzip_calibration.py` generates a lightcurve or a count-rate history from a converted CSV file. The energy thresholds can be given in the MeV unit. The usage is
```
python lightcurve_gzip.py <input file> <bin width (sec)> <p0> <p1> <lower threshold (MeV)> <upper threshold (MeV)>
```
p0 and p1 are the same as `spec_gzip_calibration.py`.

## Sample data
A sample FITS file and a converted CSV file are stored in `samples/`.
```
samples/fits/20180312_105530.fits.gz
samples/csv/20180312_105530_ch0.csv.gz
```
