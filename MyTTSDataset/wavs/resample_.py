from pydub import AudioSegment
import os

target_sample_rate = 22050

for filename in os.listdir('.'):
    if filename.endswith('.wav'):
        audio = AudioSegment.from_wav(filename)
        if audio.frame_rate != target_sample_rate:
            audio = audio.set_frame_rate(target_sample_rate)
            audio.export(filename, format='wav')
