"""
'Play sound in Python': https://pythonbasics.org/python-play-sound/

from playsound import playsound  # 1.2.2
playsound('C:\\Users\\cheet\\PycharmProjects\\Oped\\Audio\\a_summer_afternoon.mp3')

"""

from pytube import YouTube
import os
from playsound import playsound  # 1.2.2
from pydub import AudioSegment
import ffmpeg # TODO <-------------- Install ffmpeg as a codec on windows (last hope)



url = "https://www.youtube.com/watch?v=oQ2QgcRrWlc"
destination = 'C:\\Users\\cheet\\PycharmProjects\\Oped\\Audio\\'

#Remove all mp3 files in 'Audio'
audio_files = [f for f in os.listdir(destination) if os.path.isfile(os.path.join(destination, f))]
print("Removing all files in Audio...")
for af in audio_files:
    print(f"\tRemoving '{af}'")
    os.remove(f"{destination}{af}")

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -

yt = YouTube(url)
video = yt.streams.filter(only_audio=True).first()
file_name = f'{yt.title}.mp3'
file_dir = f'{destination}{file_name}'
if os.path.isfile(file_dir):
    print("Already have this downloaded")
    exit() # stand in for 'return'

out_file = video.download(output_path=destination[:-1])

base, ext = os.path.splitext(out_file)
new_file = f'{base}.mp3'
os.rename(out_file, new_file)

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# print("Converting mp3 to wav")
src = file_dir
dst = file_dir.replace('.mp3','.wav')
sound = AudioSegment.from_mp3(f'Audio\\{file_name}')
sound.export(dst, format="wav")

#  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
this_audio = [f'{destination}{f}' for f in os.listdir(destination) if os.path.isfile(os.path.join(destination, f))]
if len(this_audio) != 1:
    raise RuntimeError('Found multiple or zero audio files in Audio directory')
this_audio = this_audio[0]
print(f"Attempting to play: {this_audio}")

# sound = AudioSegment.from_mp3(this_audio)
# play(sound)
playsound(this_audio)



