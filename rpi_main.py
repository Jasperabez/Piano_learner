import mido
import time
from mido import Message
import time
import board
import neopixel
import RPi.GPIO as GPIO

# pin of pause/resume button
pinPR = 4
# pin of start/stop button
pinSS = 17
# pin of tempo up button
pinTU = 27
# pin of tempo down button
pinTD = 22
mid = mido.MidiFile("me.mid")
Tempo = 0
TempoOriginal = 0
black_notes = [61, 63, 66, 68, 70]
notes = []
noteBeat = list()
pinTime = list()
min_beat = 10
SS_state = False
PR_state = False
print("hihi")
whiteNoteList = [1, 3, 5, 6, 8, 10, 12]
blackNoteList = [2, 4, 7, 9, 11]
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# Initialize pins as pull_down
GPIO.setup(pinPR, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinTU, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinTD, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pinSS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
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

pixels = neopixel.NeoPixel(pixel_pin, num_pixels+num_pixels_black, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)


# wait for PR button to be pressed
def TogglePR(channel):
    print("TPR pressed")
    global PR_state
    PR_state = not PR_state


# increase Tempo
def TempoUp(channel):
    print("TUP pressed")
    global Tempo
    global TempoOriginal
    if Tempo > int(TempoOriginal * (1 / 10)):
        Tempo -= int(TempoOriginal * (1 / 10))


def TempoDown(channel):
    print("TUD pressed")
    global Tempo
    global TempoOriginal
    if Tempo < int(TempoOriginal * (19 / 10)):
        Tempo += int(TempoOriginal * (1 / 10))


def ToggleSS(channel):
    print("TSS pressed")
    global SS_state
    SS_state = not SS_state


print("before adding event detect")
# Pause button event listener
GPIO.add_event_detect(pinPR, GPIO.RISING, callback=TogglePR,
                      bouncetime=330)  # Setup event on pin 10 rising edge
# TempoUp button event listener
GPIO.add_event_detect(pinTU, GPIO.RISING, callback=TempoUp, bouncetime=325)
print("middle of adding event detect")
# TempoDown button event listener
GPIO.add_event_detect(pinTD, GPIO.RISING, callback=TempoDown, bouncetime=325)
# Toggle SS_state a condition in the writePin sequence, use to stop the "main" program
GPIO.add_event_detect(pinSS, GPIO.RISING, callback=ToggleSS, bouncetime=330)
print("after adding event detect")

def remap(OldValue, OldMin, OldMax, NewMin, NewMax):
    NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return NewValue


def remapNote(note):
    note_num = (note % 12) + 1
    if note_num in whiteNoteList:
        NewValue = whiteNotePins[whiteNoteList.index(note_num)]
    else:
        NewValue = blackNotePins[blackNoteList.index(note_num)]
    return NewValue


def roundBeat(input_beat):
    beat_types = {'1': 1, '2': 2, '4': 4}
    for k in beat_types:
        beat_types[k] = abs(beat_types[k] - input_beat)
    nearest_beat = min(beat_types, key=beat_types.get)
    return float(nearest_beat)


def writeToPin(sequence, temp, update_rate):
    t = 0
    pixels.fill((0, 0, 0))
    pixels.show()
    while t < (temp / (10 ** 6)):
        for note, states in sequence.items():
            if states[0] == 0 or (states[1] == 0 and (t + update_rate) >= (temp / (10 ** 6))):
                pixels[remapNote(note)] = (0, 0, 0)
            else:
                pixels[remapNote(note)] = (255, 0, 0)
            pixels.show()
        if SS_state is False:
            break
        while PR_state is True:
            if SS_state is False:
                break
            pass
        time.sleep(update_rate)
        t += update_rate


for msg in mid:
    if hasattr(msg, 'tempo') and Tempo == 0:
        Tempo = msg.tempo
        TempoOriginal = msg.tempo
    if hasattr(msg, 'type'):
        if msg.type == "note_on":
            if msg.time > Tempo / ((10 ** 6) * 8):
                beat = msg.time / (Tempo / (10 ** 6))
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
    for i in range(int(note_meta["beat"] / min_beat)):
        notedict = dict()
        if not i + 1 == int(note_meta["beat"] / min_beat):
            print("forbidden seq")
            notedict[note_meta["note"]] = (note_meta["state"], 1)
        else:
            notedict[note_meta["note"]] = (note_meta["state"], 0)
        pinTime.append(notedict)

print("SS_state = " + str(SS_state))
while True:
    while SS_state is True:
        for sequence in pinTime:
            writeToPin(sequence, Tempo, 0.1)
            if SS_state is False:
                break
            print(sequence)
        SS_state = False
    while SS_state is False:
        PR_state = False
        pixels.fill((0,10,0))
        pixels.show()
