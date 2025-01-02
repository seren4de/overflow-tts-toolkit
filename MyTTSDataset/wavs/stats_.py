import os
import wave

for filename in os.listdir('.'):
    if filename.endswith('.wav'):
        with wave.open(filename, 'r') as wav_file:
            # get the number of channels (1 for mono, 2 for stereo)
            n_channels = wav_file.getnchannels()
            # get the sample width in bytes
            sample_width = wav_file.getsampwidth()
            # get the frame rate (number of frames per second)
            frame_rate = wav_file.getframerate()
            # get the number of frames
            n_frames = wav_file.getnframes()

            print(f'File name: {filename}')
            print(f'    Number of channels: {n_channels}')
            print(f'    Sample width: {sample_width} bytes')
            print(f'    Frame rate: {frame_rate} frames per second')
            print(f'    Number of frames: {n_frames}')
