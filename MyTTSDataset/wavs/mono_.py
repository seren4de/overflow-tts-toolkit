import os
import wave
from pydub import AudioSegment

for filename in os.listdir('.'):
    if filename.endswith('.wav'):
        with wave.open(filename, 'r') as wav_file:
            n_channels = wav_file.getnchannels()
            if n_channels == 2:
                stereo_audio = AudioSegment.from_wav(filename)
                mono_audio = stereo_audio.set_channels(1)
                mono_audio.export(filename, format='wav')
