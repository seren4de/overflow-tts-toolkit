import os
import sys
from pydub import AudioSegment

def convert_mp3_to_wav(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('.mp3'):
            mp3_path = os.path.join(input_dir, filename)
            mp3_audio = AudioSegment.from_mp3(mp3_path)
            wav_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')
            mp3_audio.export(wav_path, format='wav')

if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    convert_mp3_to_wav(input_dir, output_dir)