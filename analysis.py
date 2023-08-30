#! /usr/bin/python3
#######################################################################################
#
# Program to analyze wav files - just getting started ...
#
# pip3 install librosa
#
#######################################################################################

import os
import wave
import sys
import argparse
import datetime
from fileio import parse_file_name
import numpy as np
import matplotlib.pyplot as plt

import librosa
import math

#######################################################################################

CHUNK = 1024

#######################################################################################

def read_wave_file(fname):

    if True:
        x, fs = librosa.load(fname, sr=None,mono=False)
        #print(x)
        #print(type(x),np.shape(x))
        #print(fs)
        #left  = x[0]
        #right = x[1]
        #print(len(x),len(left),len(right))
        #T=len(left)/fs
        #print(T,T/60.,T/3600.)

        #sys.exit(0)
        #return left,right,fs
        return x[0],x[1],fs
    
    # Open the input wave file
    wf = wave.open(fname, 'rb')
    fs=wf.getframerate()
    width=wf.getsampwidth()
    nchan=wf.getnchannels()
    nsamp = wf.getnframes()
    
    print('fs=',fs)
    print('width=',width)
    print('nchan=',nchan)
    print('nsamp=',nsamp)
    T=nsamp/fs
    print('T=',T,T/60.,T/3600.)
    
    # Read data
    #data = wf.readframes(CHUNK)
    data = wf.readframes(nsamp)
    wf.close()
    
    # Separate L&R channels
    nbytes=len(data)
    print('nbytes=',nbytes)
    x     = np.frombuffer(data, dtype=np.int16)
    left  = x[0::2]
    right = x[1::2]
    print(len(x),len(left),len(right))

    return left,right,fs

#######################################################################################

# Get command line args
arg_proc = argparse.ArgumentParser()

# Unflagged arg with input file name
arg_proc.add_argument('File', metavar='File',
                      type=str, default='',
                      help='Input Wave File')
args = arg_proc.parse_args()
fname=args.File
print('\nfname=',fname)

# Read data
print('Reading data ...')
left,right,fs=read_wave_file(fname)

if True:
    print('Computing spectragram ...')
    WPM=25
    Tdit=1.2/WPM
    Ndit=fs*Tdit
    print(WPM,Tdit,Ndit)
    #sys.exit(0)

    if True:
        Nwin = int(Ndit)
        Nfft = 2**math.ceil(math.log(Nwin,2))
        Nhop = int(Nwin/2)
        print(Nwin,Nfft,Nhop)
        #sys.exit(0)
    else:
        Nwin = 1024
        Nfft = Nwin
        Nhop = Nwin/2
        #n_mels = 128
    
    win = np.hanning(Nfft)
    stft= librosa.stft(left,n_fft = Nfft,hop_length = Nhop, window=win)
    out = 2 * np.abs(stft) / np.sum(win)
    print(np.shape(out))
    
    print('Plotting Spectragram...')
    plt.figure(figsize=(12, 4))
    ax = plt.axes()
    plt.set_cmap('hot')
    librosa.display.specshow(librosa.amplitude_to_db(out, ref=np.max, top_db=50),
                             y_axis='mel', x_axis='time',sr=fs)
    #y_axis='log', x_axis='time',sr=fs)
    #plt.savefig('spectrogramA.png', bbox_inches='tight', transparent=True, pad_inches=0.0 )
    plt.colorbar()
    plt.show()

    sys.exit(0)

# Plot amplitude
print('Plotting amplitude ...')
nsamp=len(left)
T=nsamp/fs
t = np.linspace(0, nsamp/fs/60.,num=nsamp)
plt.figure(figsize=(15, 5))
plt.plot(t, left)
plt.title('Left Channel')
plt.ylabel('Amplitude')
plt.xlabel('Time (min.)')
plt.xlim(0, T/60.)
plt.show()

# Plot spectragram
print('Plotting Spectragram...')
plt.figure(figsize=(15, 5))
plt.specgram(left, Fs=fs, vmin=-20, vmax=50)
plt.title('Left Channel')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.xlim(0, T)
plt.colorbar()
plt.show()

sys.exit(0)


    
