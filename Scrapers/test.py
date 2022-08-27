#Source https://github.com/jschuhmann47/youtubeToWav
import subprocess

mainDir = r'C:\Users\cheet\PycharmProjects\Oped\Audio'
src = f"{mainDir}\\cerror - Rainbow parade - 01 A summer afternoon.mp3"
dst = f"{mainDir}\\converted.wav"


subprocess.call(['ffmpeg', '-i', src, dst])
