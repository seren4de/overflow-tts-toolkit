import csv

metafile_path = "./MyTTSDataset/metadata.csv"

def ljspeech_formatter(metafile_path):
    formatted_data = []
    with open(metafile_path, 'r') as f:
        reader = csv.DictReader(f, delimiter='|', fieldnames=['ID', 'Transcription', 'Normalized Transcription'])
        for row in reader:
            formatted_data.append({
                "audio_file": f"{row['ID']}.wav",
                "text": row['Normalized Transcription'],
                "speaker_name": "LJSpeech",
                "language": "en-US"
            })
    return formatted_data