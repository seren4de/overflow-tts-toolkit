from nltk.tokenize import sent_tokenize
import os
import nltk

nltk.download('punkt')
def prepare_transcript(transcript_file, default_speaker, output_file):
    with open(transcript_file, 'r') as f:
        lines = f.readlines()
    with open(output_file, 'w') as f:
        for line in lines:
            if '\t' in line:
                speaker, text = line.split('\t', 1)
            else:
                speaker = default_speaker
                text = line
            sentences = sent_tokenize(text)
            for sentence in sentences:
                f.write(f'{speaker}\t{sentence}\n')


speaker_name = 'Speaker1'
transcript_dir = './text/input_text/'
output_dir = './corpus_directory/Speaker1/'

for file in os.listdir(transcript_dir):
    if file.endswith('.txt'):
        transcript_file = os.path.join(transcript_dir, file)
        output_file = os.path.join(output_dir, file)
        prepare_transcript(transcript_file, speaker_name, output_file)