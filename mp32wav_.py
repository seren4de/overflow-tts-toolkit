import os
import sys
from pydub import AudioSegment

def convert_mp3_to_wav(input_dir, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over the files in the input directory
    for filename in os.listdir(input_dir):
        # Check if the file is an MP3 file
        if filename.endswith('.mp3'):
            # Construct the full path to the MP3 file
            mp3_path = os.path.join(input_dir, filename)
            # Load the MP3 file using pydub
            mp3_audio = AudioSegment.from_mp3(mp3_path)
            # Construct the full path to the output WAV file
            wav_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')
            # Export the audio as a WAV file
            mp3_audio.export(wav_path, format='wav')

if __name__ == '__main__':
    # Parse the command-line arguments
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    # Convert the MP3 files to WAV format
    convert_mp3_to_wav(input_dir, output_dir)