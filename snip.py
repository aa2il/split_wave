#!/usr/bin/env -S uv run --script

# The beginnings of a script to read info from log and use it for snipping

import argparse
import os
import sys
from fileio import parse_adif
from settings import CONFIG_PARAMS


# Command line args
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument('Call', metavar='Call', nargs=1,
                      type=str, default=None,
                      help='Callsign to snip')
#arg_proc.add_argument("-port", help="Connection Port",
#                              type=int,default=0)
args = arg_proc.parse_args()

CALL=args.Call[0]
print('Call=',CALL)

# Read config file
P=CONFIG_PARAMS('.keyerrc')
#print(dir(P))
#sys.exit(0)

# Load complete cw logbook
MY_CALL2 = P.SETTINGS['MY_OPERATOR'].split('/')[0]
P.WORK_DIR=os.path.expanduser('~/'+MY_CALL2+'/')
P.LOG_FILE = P.WORK_DIR+MY_CALL2.replace('/','_')+".adif"
print('GUI: Reading ADIF log file',P.LOG_FILE)
logbook = parse_adif(P.LOG_FILE,upper_case=True,verbosity=0)

# Look for the last QSO with this call
last_qso=None
for qso in logbook:
    if qso['CALL']==CALL:
        print(qso)
        last_qso=qso

print('\nlast qso=',last_qso,'\n')
t=last_qso['TIME_OFF']
d=last_qso['QSO_DATE_OFF']
f="capture_"+d+"*.wav"
print('t=',t,'\td=',d,'\tf=',f)

cmd="rm -r SNIPPIT.wav ; ~/Python/split_wave/split_wave.py "+f+" -snip "+t
print('\ncmd=',cmd)
os.system(cmd)

cmd2='audacity SNIPPIT.wav'
print('\ncmd2=',cmd2)
os.system(cmd2)
