# sonificationscript
Script to sonify data. This script might need ample modification depending on the type of data you work with. However it gives an overview of how to convert frequency data that is not in the audible range to sonified sound samples.

Providing data in numerical format as an np.array one can use this script to sonify  numerical data. 

What it does:
First it creates a midi file from the numerical data mapping the values to pitch and tempo using MidiTime library.
Secondly it takes the created midi files and uses Fluidsynth a synthesizer to map the information in the midi to a soundfont, that is using soundsamples and the information in the midifile sonification is done.

Possible modification of path to soundfont etc. necessary to use it.

Dependencies:

MidiTime https://github.com/cirlabs/miditime
Fluidsynth https://sourceforge.net/p/fluidsynth/wiki/LowLatency/
