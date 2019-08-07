import mido
from mido import Message
mid = mido.MidiFile("me.mid")
Tempo = 0
noteBeat = list()
print("hihi")

for msg in mid:
    print(msg)