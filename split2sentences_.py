import os
import sys
from pydub import AudioSegment
from pydub.silence import split_on_silence
from praatio import tgio

def prepare_dataset(corpus_dir):
    # Create the output directories if they don't exist
    os.makedirs('./MyTTSDataset/wavs', exist_ok=True)

    # Open the metadata file for writing
    with open('./MyTTSDataset/metadata.txt', 'w') as metadata_file:
        # Iterate over the speakers in the corpus directory
        for speaker in os.listdir(corpus_dir):
            speaker_dir = os.path.join(corpus_dir, speaker)
            if os.path.isdir(speaker_dir):
                # Iterate over the transcript files in the speaker directory
                for transcript_file in os.listdir(speaker_dir):
                    if transcript_file.endswith('.txt'):
                        base_name = os.path.splitext(transcript_file)[0]
                        textgrid_file = os.path.join(speaker_dir, base_name + '.TextGrid')
                        wav_file = os.path.join(speaker_dir, base_name + '.wav')

                        # Load the transcript, TextGrid, and audio data
                        with open(os.path.join(speaker_dir, transcript_file), 'r') as f:
                            transcript = f.read().strip()
                        tg = tgio.openTextgrid(textgrid_file)
                        audio = AudioSegment.from_wav(wav_file)

                        # Split the audio into sentences using the TextGrid data
                        entryList = tg.tierDict[tg.tierNameList[0]].entryList
                        sentence_start = None
                        sentence_end = None
                        sentence_words = []
                        sentences = []
                        transcriptions = []
                        for start, end, label in entryList:
                            if label == "speaker1":
                                if sentence_start is not None:
                                    sentences.append(audio[int(sentence_start * 1000):int(sentence_end * 1000)])
                                    transcriptions.append(' '.join(sentence_words))
                                sentence_start = start
                                sentence_end = end
                                sentence_words = []
                            elif sentence_start is not None:
                                sentence_end = end
                                sentence_words.append(label)
                        if sentence_start is not None:
                            sentences.append(audio[int(sentence_start * 1000):int(sentence_end * 1000)])
                            transcriptions.append(' '.join(sentence_words))

                        # Write each sentence audio and its transcription to the output files
                        for i, (sentence, transcription) in enumerate(zip(sentences, transcriptions)):
                            sentence_file = f'{base_name}_{i+1}.wav'
                            sentence_path = f'./MyTTSDataset/wavs/{sentence_file}'
                            sentence.export(sentence_path, format='wav')
                            metadata_file.write(f'{sentence_file}|{transcription}\n')

if __name__ == '__main__':
    corpus_dir = sys.argv[1]
    prepare_dataset(corpus_dir)
