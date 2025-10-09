#! /home/joea/miniconda3/envs/aa2il/bin/python -u
#
# NEW: /home/joea/miniconda3/envs/aa2il/bin/python -u
# OLD: /usr/bin/python3 -u 
################################################################################
#
# split_wave.py - Rev 1.0
# Copyright (C) 2021-5 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# Program to split up a capture wave file
#
# This file was accidently deleted shortly after I got it working.
# It was recovered using:
#
# sudo ext4magic /dev/sdb2 -r -f /home/joea/Python/sound/split_wave.py -d /data2/data/junk
#
# Notes:
#           pip3 install pydub
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

import os
import wave
import sys
import argparse
from datetime import datetime,timedelta
from fileio import parse_file_name
import numpy as np
import librosa
from utilities import error_trap

################################################################################

CHUNK = 1024

################################################################################

# Get command line args
arg_proc = argparse.ArgumentParser()

# Unflagged arg with input file name(s)
arg_proc.add_argument('File', metavar='File',nargs='*',
                      type=str, default='',
                      help='Input Wave File')
arg_proc.add_argument("-snip", help='Extract a snippet, time or time interval',
                      type=str,default=None,nargs='*')
arg_proc.add_argument("-date", help='Date fopr snippet',
                      type=str,default=None)

args = arg_proc.parse_args()
fnames=args.File
if len(fnames)==0:
    fnames=['capture_*.wav']

DATE = args.date
TIME = np.array(args.snip)
#if np.isscalar(t):
#    t = np.array( [t-1, t+1] )            # +/- 1 min around given time
#if len(t)==1:
#    t = np.array( [t[0]-1, t[0]+1] )            # +/- 1 min around given time

print('\nfnames=',fnames)
print('TIME=',TIME)
print('DATE=',DATE)
#sys.exit(0)

################################################################################

# Loop through list of input files
success=False
for f in fnames:
    fname_in = os.path.expanduser(f)
    p,n,ext  = parse_file_name(fname_in)

    print('\nfname_in=',fname_in,'\np=',p,'\tn=',n,'ext=',ext)
    if not fname_in:
        print("Split a wave file into hour long segments.\n\nUsage: %s -i filename.wav" % sys.argv[0])
        sys.exit(-1)

    elif ext=='.mp3' and True:           # Until we get mp support working properly
        
        print('\nNeed to convert to wave file first:')
        cmd='mpg123 -v -w '+n+'.wav '+n+'.mp3'
        print('\n'+cmd+'\n')
        os.system(cmd)
        print('\nDone.\n')
        #sys.exit(-1)

    # Find time stamp
    a=fname_in.split('_')
    b=a[2].split('.')
    ext=b[1]
    ext='wav'                  # Until we get mp3 working properly
    fname2=p+n+'.'+ext
    print('fname2=',fname2)
    print('a=',a)
    print('b=',b)

    start_time = datetime.strptime( a[1]+' '+b[0], "%Y%m%d %H%M%S")
    print('start_time=',start_time)

    # Open the input file
    if ext=='wav':
        try:
            wf = wave.open(fname2, 'rb')
        except:
            error_trap('SPLIT WAVE: Unable to open '+fname2)
            continue
        fs=wf.getframerate()
        width=wf.getsampwidth()
        nchan=wf.getnchannels()

        print('fs=',fs)
        print('width=',width)
        print('nchan=',nchan)
        nframes=wf.getnframes()
        dt=CHUNK/fs
        print('CHUNK=',CHUNK,'\tdt=',dt)
        dt2=nframes/fs
        print('nframes=',nframes,'\tdt2=',dt2,'sec =',dt2/60.,'min = ',dt2/3600.,'hrs')
        
        end_time = start_time + timedelta(seconds=dt2)
        print('end_time=',end_time)
        #sys.exit(0)

    # Extract a snippet
    if args.snip:
        t=TIME
        print('SNIP SNIP t=',t,'\tlen=',len(t),len(t[0]))
        
        if len(t[0])==4:
            if len(t)==1:
                t=[t[0]+'00']
            else:
                t=[t[0]+'00',t[1]]

        if DATE==None:
            DATE2=a[1]
        elif len(DATE)<8:
            DATE2=a[1][:8-len(DATE)]+DATE
        print('DATE2=',DATE2)
                
        t1 = datetime.strptime( DATE2+' '+t[0], "%Y%m%d %H%M%S")
        
        if len(t)==1:
            dt = timedelta(seconds=60)
            t2 = t1 + dt
            t1 = t1 - dt
        else:
            if len(t[1])==4:
                t=[t[0],t[1]+'00']
            t2 = datetime.strptime( a[1]+' '+t[1], "%Y%m%d %H%M%S")

        # Check if this interval is in this file
        if t2<start_time or t1>end_time:
            print('Time interval not in this file!')
            print('\tt1=',t1)
            print('\tt2=',t2)
            continue
            #sys.exit(0)

        # Check for date roll-over - kudged for now - Probably don't get here anymore!
        if t1<start_time:
            print('WARNING - Likely date roll-over - kludged!!!!!!!!!')
            t1 += timedelta(hours=24)
            t2 += timedelta(hours=24)
            
        start = (t1-start_time).total_seconds()
        end   = (t2-start_time).total_seconds()

        print('t1=',t1,t1>=start_time,start)
        print('t2=',t2,end)

        fname_out = t1.strftime("SNIPPIT_%Y%m%d_%H%M%S.wav")
        fname_out = "SNIPPIT.wav"
        print('fname_out=',fname_out)
        
        #sys.exit(0)

        
        if ext=='wav':
            
            # Set position in wave to start of segment & extract data
            try:
                wf.setpos(int(start * fs))
            except: 
                error_trap('SPLIT WAVE: Unable to set file position')
                continue
                
            data = wf.readframes(int((end - start) * fs))
            print('data=',type(data),len(data))
            
        elif ext=='mp3':

            data, fs = librosa.load(fname2,offset=start,duration=(end-start),sr=None)
            print('fs=',fs)
            print(type(data),np.shape(data),type(data[0]))
            width=2
            nchan=2

            if True:
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                ax.plot(data[0::2])
                plt.show()
                #data=np.array(data)
                #print(type(data),np.shape(data),type(data[0,0]))
                sys.exit(0)
            else:
                data=(32767*data).astype(np.int16)
                print(data[:10])
                print(data[:10].tobytes())
            
            #sys.exit(0)

            """
            # This seem really slow!
            from pydub import AudioSegment
            #from pydub.utils import get_array_type
            
            data = AudioSegment.from_file(file=fname2)
            print(type(data),np.shape(data))
            print(data[:10])
            sys.exit(0)
            """
            
        else:
    
            print('HELP!')
            sys.exit(0)

        # Write out data

        if False:
            import wavio
            wavio.write(fname_out, data, fs, sampwidth=2)
        else:        
            wf2 = wave.open(fname_out, 'wb')
            wf2.setnchannels(nchan)
            wf2.setsampwidth(width)
            wf2.setframerate(fs)
            wf2.setnframes(int(len(data) / width))
            #wf2.writeframes(data.tobytes())
            wf2.writeframes(data)
            wf2.close()

            if args.snip:
                break
            
        # Skip over next section which was the original code to break-up a large file
        continue

    # This next section was the original code to break-up a large file into smaller (1hr) chunks.
    # It should still work but might need to add .mp3 code as well.
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
            wf2.setnchannels(nchan)
            wf2.setsampwidth(width)
            wf2.setframerate(fs)

        # Copy this chunk
        wf2.writeframes(data)
        t += timedelta(seconds=dt)

        # Read next chunk
        data = wf.readframes(CHUNK)

    # Get ready for the next file
    wf.close()
    wf2.close()
    
#sys.exit(0)


    
