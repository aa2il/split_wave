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
# Notes:
#           pip3 install pydub
#
#######################################################################################

import os
import wave
import sys
import argparse
from datetime import datetime,timedelta
from fileio import parse_file_name
import numpy as np
import librosa

#######################################################################################

CHUNK = 1024

#######################################################################################

# Get command line args
arg_proc = argparse.ArgumentParser()

# Unflagged arg with input file name(s)
arg_proc.add_argument('File', metavar='File',nargs='+',
                      type=str, default='',
                      help='Input Wave File')
arg_proc.add_argument("-snip", help='Extract a snippet',
                      type=str,default=None,nargs='*')

args = arg_proc.parse_args()
fnames=args.File

t = np.array(args.snip)
#if np.isscalar(t):
#    t = np.array( [t-1, t+1] )            # +/- 1 min around given time
#if len(t)==1:
#    t = np.array( [t[0]-1, t[0]+1] )            # +/- 1 min around given time

print('\nfnames=',fnames)
print('t=',t)
#sys.exit(0)

#######################################################################################

# Loop through list of input files
for f in fnames:
    fname_in = os.path.expanduser(f)
    p,n,ext  = parse_file_name(fname_in)

    print('fname_in=',fname_in,'\np=',p,'\tn=',n,'ext=',ext)
    if not fname_in:
        print("Split a wave file into hour long segments.\n\nUsage: %s -i filename.wav" % sys.argv[0])
        sys.exit(-1)

    elif ext=='.mp3' and False:
        
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
    fname2=p+n+'.'+ext
    print('fname2=',fname2)
    print('a=',a)
    print('b=',b)

    start_time = datetime.strptime( a[1]+' '+b[0], "%Y%m%d %H%M%S")
    print('start_time=',start_time)

    # Open the input file
    if ext=='wav':
        wf = wave.open(fname2, 'rb')
        fs=wf.getframerate()
        width=wf.getsampwidth()
        nchan=wf.getnchannels()

        print('fs=',fs)
        print('width=',width)
        print('nchan=',nchan)
        dt=CHUNK/fs
        print('dt=',dt)

    # Extract a snippet
    if args.snip:
        print('SNIP SNIP',t,len(t),len(t[0]))
        
        if len(t[0])==4:
            if len(t)==1:
                t=[t[0]+'00']
            else:
                t=[t[0]+'00',t[1]]
        t1 = datetime.strptime( a[1]+' '+t[0], "%Y%m%d %H%M%S")
        
        if len(t)==1:
            dt = timedelta(seconds=60)
            t2 = t1 + dt
            t1 = t1 - dt
        else:
            if len(t[1])==4:
                t=[t[0],t[1]+'00']
            t2 = datetime.strptime( a[1]+' '+t[1], "%Y%m%d %H%M%S")

        # Check for date roll-over - kudged for now
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
            
            # set position in wave to start of segment & extract data
            wf.setpos(int(start * fs))
            data = wf.readframes(int((end - start) * fs))
            print(type(data),len(data))
            
        elif ext=='mp3':

            data, fs = librosa.load(fname2,offset=start,duration=(end-start))
            print('fs=',fs)
            print(type(data),np.shape(data))
            width=2
            nchan=2

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

        """ 
        # Try this sometime
        import wavio
        wavio.write("myfile.wav", my_np_array, fs, sampwidth=2)
        """
        
        wf2 = wave.open(fname_out, 'wb')
        wf2.setnchannels(nchan)
        wf2.setsampwidth(width)
        wf2.setframerate(fs)
        wf2.setnframes(int(len(data) / width))
        wf2.writeframes(data)
        wf2.close()

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


    
