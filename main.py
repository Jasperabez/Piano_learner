import mido
import time
from mido import Message
mid = mido.MidiFile("me.mid")
Tempo = 0
notes = []
noteBeat = list()
pinTime = list()
min_beat = 10
print("hihi")


def remap(OldValue,OldMin,OldMax,NewMin,NewMax):
    NewValue = (((OldValue - OldMin) * (NewMax - NewMin)) / (OldMax - OldMin)) + NewMin
    return NewValue


def roundBeat(input_beat):
    beat_types = {'1': 1, '2': 2, '4': 4}
    for k in beat_types:
        beat_types[k] = abs(beat_types[k]-input_beat)
    nearest_beat = min(beat_types, key=beat_types.get)
    return float(nearest_beat)


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
    for i in range(int(note_meta["beat"]/min_beat)):
        notedict = dict()
        if not i+1 == int(note_meta["beat"]/min_beat):
            notedict[note_meta["note"]] = (note_meta["state"], 1)
        else:
            notedict[note_meta["note"]] = (note_meta["state"], 0)
        pinTime.append(notedict)

for sequence in pinTime:
    print(sequence.key())