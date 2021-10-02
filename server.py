import os

file = _FILES("file1")
if(file):
    os.rename(file,"song.mp3")
    print("song.mp3")