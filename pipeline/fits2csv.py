#!/usr/bin/env python
import astropy.io.fits as fitsio
import numpy as np
import datetime
import math
import sys
import os

# functions
def gps_status_test(string):
    if (string=="GP") or (string=="NULL"):
        gps_status=False
    else:
        gps_status=True
    return gps_status

def gps_base_time(gps):
    time_tag_base=int(gps[0][0])&0xFFFFFFFFFF
    unixtime_base=float(gps[0][1])
    gps_string_base=gps[0][2][8:14]
    time_obj_unixtime=datetime.datetime.fromtimestamp(unixtime_base, datetime.timezone.utc)
    time_str_gps=time_obj_unixtime.strftime("%Y%m%d")+" "+gps_string_base+"+00:00"
    time_obj_precise=datetime.datetime.strptime(time_str_gps, "%Y%m%d %H%M%S%z")+datetime.timedelta(seconds=1.0)
    delta_time_gps=time_obj_unixtime-time_obj_precise
    if (delta_time_gps.total_seconds()>12.0*3600.0):
        time_obj_precise=time_obj_precise+datetime.timedelta(days=1.0)
    elif (delta_time_gps.total_seconds()<-12.0*3600.0):
        time_obj_precise=time_obj_precise-datetime.timedelta(days=1.0)
    unixtime_precise=time_obj_precise.timestamp()
    clock=clock_verification(gps)
    time_standard=[unixtime_precise, time_tag_base, clock]
    return time_standard

def non_gps_base_time(filename, event, gps):
    time_str_file=(os.path.basename(filename).split('.', 1)[0])+"+00:00"
    time_obj_file=datetime.datetime.strptime(time_str_file, "%Y%m%d_%H%M%S%z")
    time_obj_gps=datetime.datetime.fromtimestamp(float(gps[0][1]), datetime.timezone.utc)
    delta_time_obj=time_obj_gps-time_obj_file
    time_lag_hour=round((delta_time_obj.total_seconds())/3600.0)
    time_obj_file=time_obj_file+datetime.timedelta(hours=time_lag_hour)
    time_standard=[time_obj_file.timestamp(), int(event[0][1]), 1.0e8]
    return time_standard

def detect_counter_loop(event):
    start_count=event["timeTag"][0]
    end_count=event["timeTag"][len(event)-1]
    if start_count>end_count:
        detect=True
    else:
        detect=False
    return detect

def check_loop(array, maximum):
    if (array[0]>array[array.size-1]):
        noloop=array[array>=array[0]]
        loop=array[array<array[0]]
        loop+=maximum
        narray=np.concatenate([noloop, loop])
        return narray
    else:
        return array

def extract_data(adc_channel, event, time_standard):
    clock=time_standard[2]
    data_mask_channel=event[(event["boardIndexAndChannel"]==adc_channel)]
    if (len(data_mask_channel)!=0):
        unixTime=np.array(data_mask_channel["timeTag"], np.float64)
        phaMax=np.array(data_mask_channel["phaMax"], np.int32)
        triggerCount=np.array(data_mask_channel["triggerCount"], np.int32)
        unixTime=check_loop(unixTime, 2.0**40)
        triggerCount=check_loop(triggerCount, 2**16)
        phaMax=phaMax-2048
        unixTime=time_standard[0]+(unixTime-time_standard[1])/clock
        triggerCountShift=np.roll(triggerCount, 1)
        deadCount=triggerCount-triggerCountShift-1
        deadCount[0]=0
        data=np.stack([unixTime, phaMax, deadCount])
        return data
    else:
        return np.array([0])

def gps_verification(input_file, fits_file):
    event=fits_file[1].data
    if len(fits_file)<3:
        print("Warning: This FITS file is not properly finalized. Pipeline stopped.")
        gps_status=False
        exit()
    else:
        gps=fits_file[2].data
        gps_status=gps_status_test(gps[0][2])
    if (gps_status==True):
        time_standard=gps_base_time(gps)
    else:
        time_standard=non_gps_base_time(input_file, event, gps)
    return time_standard

def check_file(file):
    if (os.path.exists(file)==False):
        print(file, "does not exist.")
        exit()

def clock_verification(gps):
    clock=1.0e8
    time_tag=np.array([gps[0][0]], dtype="int64")
    for i in range(1, len(gps)):
        if (gps[i][2]!="NULL") and (gps[i][2]!=""):
            time_tag=np.append(time_tag, gps[i][0])
    time_tag=time_tag&0xFFFFFFFFFF
    time_tag=check_loop(time_tag, 2**40)
    if (time_tag.size<2):
        return clock
    else:
        second=float(time_tag[time_tag.size-1]-time_tag[0])/clock
        second_precise=round(second)
        clock_precise=float(time_tag[time_tag.size-1]-time_tag[0])/float(second_precise)
        rate=(clock_precise-clock)/clock
        if (abs(rate)>1.0e-4):
            return clock
        else:
            return clock_precise
        
# reading argiment parameters                                                                       
args=sys.argv
if len(args)<1:
    print("Error: invalid number of arguments")
    print("Usage: python fits2csv.py <input file> <output directory>")
    exit()

# reading fits file
input_file=args[1]
output_dir=args[2]
check_file(input_file)
check_file(output_dir)
fits_file=fitsio.open(input_file)
event=fits_file[1].data
time_standard=gps_verification(input_file, fits_file)

# main process
for adc in range(4):
    data=extract_data(adc, event, time_standard)
    output_file=output_dir+"/"+(os.path.basename(input_file).split('.', 1)[0])+"_ch"+str(adc)+".csv.gz"
    if (data.size>1):
        np.savetxt(output_file, data.transpose(), fmt=["%.6f", "%d", "%d"], delimiter=",")
