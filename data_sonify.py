import os
import gc
import subprocess
import re

# file handling
import pandas as pd
import csv
# numerical
import numpy as np
import scipy
from scipy.signal import argrelextrema
from decimal import Decimal

# visualizing
import matplotlib.pyplot as plt

# audio
import pyaudio
from DataSounds.sounds import get_music, w2Midi
from mido import MidiFile
from miditime.miditime import MIDITime
from datetime import datetime
import random

# quality of audio depends on
samplingrate = 1000# sampling rate in Hz
# parameterhandling

'''
This is a script for data sonification provided one provides data in form of
an array that contains a complex wave form sonification of numerical data with this
script is possible
'''

#
# copy to get mass ranges and indizes that are relevant i.e. only masses that are
# within the non noise range i.e. 100.1, 200.2, 300.3 etc. exclude everything else
# look at first significant digit after comma
Amplitudes = [10000000, 20000000]

steadyamp = 10000000

# now sepearte all nominal masses

def createsines(steadyamp, Amplitudes, samplingrate):
    '''automatically generates linear combinations of sine waves that are generated using
    frequencies and intensities within a nominal mass'''
    sumsinesarray = []
    for i in range(len(Amplitudes)):
                    # in case it is the first sine wave to be created
                samplingrate = samplingrate # sampling rate in Hz
                # samples exactly half of one period because 1/20 is 0.05
                # then we would have a whole period sampled with 0.05
                t = np.arange(0, 5.0, 1.0/samplingrate)
                freqarray = [20, 300, 555, 100]
                A1 = steadyamp
                A2 = Amplitudes[i]
                A3 = steadyamp
                A4 = steadyamp
                # A3 = steadyamp
                # A4 = steadyamp
                freq = freqarray[0]
                period = int(samplingrate/freq)
                y1 = A1 * np.sin(2 * np.pi * freqarray[0] * t)
                y2 = A2 * np.sin(2 * np.pi * freqarray[1] * t)
                y3 = A3 * np.sin(2 * np.pi * freqarray[2] * t)
                y4 = A4 * np.sin(2 * np.pi * freqarray[3] * t)
                sumsine = y1 + y2 + y3 + y4
                print('sumesine array')
                print(sumsine)
                name = str(Amplitudes[i])

                sumsinesarray.append([sumsine, name])
    return  sumsinesarray




###############################################################################
#
# Preprocessing End
#
#################################################################################3


###############################################################################
#
# Validation Start
#
#################################################################################3

# needs to be a global variable

def midify(sumsinearray):
    counter = 0
    global mymidi
    for i in range(len(sumsinearray)):
        name = str(sumsinearray[i][1]) +'.mid'
        mymidi = MIDITime(120, name, 4, 5, 1)
        my_data = dictify(sumsinearray[i][0])
        my_data_timed = [{'beat': mymidi.beat(d['datapoint']), 'magnitude': d['magnitude']} for d in my_data]
        start_time = my_data_timed[0]['beat']
        note_list = builtnotelist(my_data_timed, start_time)
    # Add a track with those notes
        mymidi.add_track(note_list)
    # Output the .mid file
        mymidi.save_midi()
        counter += 1


def getmaxandmin(my_data_timed):
    seq = [x['magnitude'] for x in my_data_timed]
    mini = min(seq)
    maxi = max(seq)
    return maxi, mini

# Instantiate the class with a tempo (120bpm is the default) and an output file destination.
# 0.5 seconds per time step,  base octave is C5 , output range over 1 octave

def mag_to_pitch_tuned(magnitude, my_data_timed):
    # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
    maxi, mini = getmaxandmin(my_data_timed)
    scale_pct = mymidi.linear_scale_pct(mini, maxi, magnitude)
    # Another option: Linear scale, reverse order
    # scale_pct = mymidi.linear_scale_pct(3, 5.7, magnitude, True)
    # Another option: Logarithmic scale, reverse order
    # scale_pct = mymidi.log_scale_pct(3, 5.7, magnitude, True)
    # Pick a range of notes. This allows you to play in a key.
    c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    #Find the note that matches your data point
    note = mymidi.scale_to_note(scale_pct, c_major)
    #Translate that note to a MIDI pitch
    midi_pitch = mymidi.note_to_midi_pitch(note)
    return midi_pitch

def builtnotelist(my_data_timed, start_time):
    note_list = []
    for d in my_data_timed:
        note_list.append([
            d['beat'] - start_time,
            mag_to_pitch_tuned(d['magnitude'], my_data_timed),
            100,  # attack
            1  # duration, in beats
            ])
    return note_list


###############################################################################
#
# Preprocessing End
#
#################################################################################3

################################################################################
#
# Sonification Start
#
##################################################################################
def dictify(sumsine):
    dictlist = []
    dicti = {}
    counter = 0
    rangearray = range(len(sumsinearray[0][0]))
    tuples = zip(rangearray, sumsine)
    for x in tuples:
        zipped = dict(zip(('datapoint', 'magnitude'), x))
        dictlist.append(zipped)
        counter += 1
    return dictlist



# mididirectory
mididirectory = os.getcwd()

# # now use soundfonts to add synthesized sounds to the midi file
def sonify(mididirectory):
    ''' to_audio takes arguments: filepath to soundfont file, filepath for midifile to convert, outputpath
    , fileformat for output, text file with the original index of the files so they can be associated with the samples
    for naming, append false replaces the filename with'''
    files = os.listdir(mididirectory)
    print(files)
    # finds all digits
    regex = re.compile(r'\d+')
    counter = 0
    subprocess.call('bash audio start', shell=True)
    for i in files:

        if i.endswith('.mid'):
            infile = i
            samplenum = regex.findall(infile)
            cwd = os.getcwd()
            outfile = cwd + '/sonified/sonified'+ str(samplenum[0]) +'.wav'
            print("sonifying midifile named " + str(samplenum) +' running number ' + str(counter))
            cmd = 'fluidsynth -F ' + outfile + ' /usr/share/sounds/sf2/FluidR3_GM.sf2 ' + infile
            print(cmd)
            subprocess.call(cmd, shell=True)
            counter += 1
        # 'fluidsynth -F output.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 sample.midi'
        # finalizes audio server
    subprocess.call('bash audio stop', shell=True)
    return





###############################################################################
#
# Sonification End
#
#################################################################################3

################################################################################
#
# Feature extraction Start
#
##################################################################################

# later on main for preprocessing
sumsinearray= createsines(steadyamp, Amplitudes, samplingrate)

# create midi from numerical data
midify(sumsinearray)

# main for sonify
sonify(mididirectory)
