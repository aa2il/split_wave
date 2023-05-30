#! /usr/bin/python3
#######################################################################################
#
# Program to split up a capture wave file
#
# This file was accidently deleted shortly after I got it working.
# It was recovered using:
#
# sudo ext4magic /dev/sdb2 -r -f /home/joea/Python/sound/split_wave.py -d /data2/data/junk
#
#######################################################################################

import os
import wave
import sys
import argparse
import datetime
from fileio import parse_file_name

#######################################################################################

CHUNK = 1024

#######################################################################################

# Get command line args
arg_proc = argparse.ArgumentParser()

# Unflagged arg with input file name(s)
arg_proc.add_argument('File', metavar='File',nargs='+',
                      type=str, default='',
                      help='Input Wave File')
args = arg_proc.parse_args()
fnames=args.File
print('fnames=',fnames)

# Loop through list of input files
for f in fnames:
    fname_in = os.path.expanduser(f)
    p,n,ext  = parse_file_name(fname_in)

    print('fname_in=',fname_in,'\np=',p,'\tn=',n,'ext=',ext)
    if not fname_in:
        print("Split a wave file into hour long segments.\n\nUsage: %s -i filename.wav" % sys.argv[0])
        sys.exit(-1)

    elif ext=='.mp3':
        print('\nNeed to convert to wave file first:')
        cmd='mpg123 -v -w '+n+'.wav '+n+'.mp3'
        print('\n'+cmd+'\n')
        os.system(cmd)
        print('\nDone.\n')
        #sys.exit(-1)

    # Find time stamp
    a=fname_in.split('_')
    b=a[2].split('.')
    fname2=p+n+'.wav'
    print('fname2=',fname2)
    print('a=',a)
    print('b=',b)

    start_time = datetime.datetime.strptime( a[1]+' '+b[0], "%Y%m%d %H%M%S")
    print('start_time=',start_time)

    # Open the input wave file
    wf = wave.open(fname2, 'rb')
    fs=wf.getframerate()
    width=wf.getsampwidth()
    channels=wf.getnchannels()

    print('fs=',fs)
    dt=CHUNK/fs
    print('dt=',dt)

    # Read data
    data = wf.readframes(CHUNK)
    t=start_time
    hour=-1
    wf2=None
    while len(data) > 0:

        # Check for next hour
        if t.hour!=hour:
            fname_out = t.strftime("SPLIT_%Y%m%d_%H%M%S.wav")
            print('t=',t,'\thour=',t.hour,hour,'\t',fname_out)
            hour=t.hour

            # Close out prior output file ...
            if wf2:
                wf2.writeframes(data)
                wf2.close()

            # ... and open a new one
            wf2 = wave.open(fname_out, 'wb')
            wf2.setnchannels(channels)
            wf2.setsampwidth(width)
            wf2.setframerate(fs)

        # Copy this chunk
        wf2.writeframes(data)
        t += datetime.timedelta(seconds=dt)

        # Read next chunk
        data = wf.readframes(CHUNK)

    # Get ready for the next file
    wf.close()
    wf2.close()
    
#sys.exit(0)


    
