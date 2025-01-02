import os
import sys
from pydub import AudioSegment
from pydub.silence import split_on_silence
from praatio import tgio

def prepare_dataset(corpus_dir):
    os.makedirs('./MyTTSDataset/wavs', exist_ok=True)

    with open('./MyTTSDataset/metadata.txt', 'w') as metadata_file:
        for speaker in os.listdir(corpus_dir):
            speaker_dir = os.path.join(corpus_dir, speaker)
            if os.path.isdir(speaker_dir):
                for transcript_file in os.listdir(speaker_dir):
                    if transcript_file.endswith('.txt'):
                        base_name = os.path.splitext(transcript_file)[0]
                        textgrid_file = os.path.join(speaker_dir, base_name + '.TextGrid')
                        wav_file = os.path.join(speaker_dir, base_name + '.wav')
                        with open(os.path.join(speaker_dir, transcript_file), 'r') as f:
                            transcript = f.read().strip()
                        tg = tgio.openTextgrid(textgrid_file)
                        audio = AudioSegment.from_wav(wav_file)
                        
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
                        
                        for i, (sentence, transcription) in enumerate(zip(sentences, transcriptions)):
                            sentence_file = f'{base_name}_{i+1}.wav'
                            sentence_path = f'./MyTTSDataset/wavs/{sentence_file}'
                            sentence.export(sentence_path, format='wav')
                            metadata_file.write(f'{sentence_file}|{transcription}\n')

if __name__ == '__main__':
    corpus_dir = sys.argv[1]
    prepare_dataset(corpus_dir)
