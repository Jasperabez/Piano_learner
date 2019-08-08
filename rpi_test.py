import mido
import time
from mido import Message
import time
import board
import neopixel
import RPi.GPIO as GPIO

mid = mido.MidiFile("me.mid")
Tempo = 0
black_notes = [61,63,66,68,70]
notes = []
noteBeat = list()
pinTime = list()
min_beat = 10
switch_state = 0;
print("hihi")
whiteNoteList = [1,3,5,6,8,10,12]
blackNoteList = [2,4,7,9,11]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#pin of start/pause/resume button
GPIO.setup(25,GPIO.IN)
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18
# The number of NeoPixels
num_pixels = 7
num_pixels_black = 5
whiteNotePins = list(range(num_pixels))
blackNotePins = list(range(num_pixels_black))
for value in blackNotePins:
    value += 7
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)

def remap(OldValue,OldMin,OldMax,NewMin,NewMax):
    NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return NewValue

def remapNote(note):
    note_num = (note%12)+1
    if note_num in whiteNoteList:
        NewValue = whiteNotePins[whiteNoteList.index(note_num)]
    else:
        NewValue = blackNotePins[blackNoteList.index(note_num)]
    return NewValue

def roundBeat(input_beat):
    beat_types = {'1': 1, '2': 2, '4': 4}
    for k in beat_types:
        beat_types[k] = abs(beat_types[k]-input_beat)
    nearest_beat = min(beat_types, key=beat_types.get)
    return float(nearest_beat)

def writeToPin(sequence, temp):
    pixels.fill((0,0,0))
    pixels.show()
    for note,state in sequence.items():
        if state ==0:
            pixels[remapNote(note)] = (0, 0, 0)
        else:
            pixels[remapNote(note)] = (255, 0, 0)
        pixels.show()
    time.sleep(temp / (10 ** 6))

def waitForButtonPress():
    while not GPIO.input(25):
        pass

for msg in mid:
    if hasattr(msg, 'tempo') and Tempo == 0:
        Tempo = msg.tempo
    if hasattr(msg, 'type'):
        if msg.type == "note_on":
            if msg.time > Tempo/((10**6)*8):
                beat = msg.time/(Tempo/(10**6))
                beat = roundBeat(beat)
                noteBeat.append({"note": msg.note, "beat": beat, "state": 1})
        elif msg.type == "note_off":
            noteBeat.append({"note": msg.note, "beat": 0, "state": 0})

for note_meta in noteBeat:
    if note_meta["beat"] < min_beat:
        min_beat = note_meta["beat"]
    if note_meta["note"] not in notes:
        notes.append(note_meta["note"])

for note_meta in noteBeat:
    notedict = dict()
    notedict[note_meta["note"]] = note_meta["state"]
    for i in range(int(note_meta["beat"]/min_beat)):
        pinTime.append(notedict)

while True:
    for sequence in pinTime:
      writeToPin(sequence, Tempo)
    pixels.fill((0,0,0))
    time.sleep(5)