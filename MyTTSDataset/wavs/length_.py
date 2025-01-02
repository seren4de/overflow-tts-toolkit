import os
import wave
import contextlib

lengths = {}

for filename in os.listdir('.'):
    if filename.endswith('.wav'):
        with contextlib.closing(wave.open(filename,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            if duration in lengths:
                lengths[duration].append(filename)
            else:
                lengths[duration] = [filename]

for length, files in sorted(lengths.items(), key=lambda x: x[0], reverse=True):
    print(f'{length:.2f}s: {len(files)}')
    for file in files:
        print(f'    {file}')

