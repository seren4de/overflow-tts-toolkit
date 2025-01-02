import csv
from num2words import num2words
import re

def expand_numbers(text):
    # regular expression to find numbers in the text
    pattern = re.compile(r'\b\d[\d,.]*\b')
    # find all numbers in the text
    numbers = re.findall(pattern, text)
    # replace each number with its expanded form
    for number in numbers:
        # remove commas and convert to float
        num = float(number.replace(',', ''))
        # convert number to words
        num_words = num2words(num, lang='en')
        # replace number with words in the text
        text = text.replace(number, num_words)
    return text

def add_normalized_transcription_column(metafile_path, output_path):
    with open(metafile_path, 'r') as f_in, open(output_path, 'w') as f_out:
        reader = csv.DictReader(f_in, delimiter='|', fieldnames=['ID', 'Transcription'])
        writer = csv.DictWriter(f_out, delimiter='|', fieldnames=['ID', 'Transcription', 'Normalized Transcription'])
        for row in reader:
            normalized_transcription = expand_numbers(row['Transcription'])
            writer.writerow({
                'ID': row['ID'],
                'Transcription': row['Transcription'],
                'Normalized Transcription': normalized_transcription
            })

if __name__ == '__main__':
    metafile_path = "./MyTTSDataset/metadata.csv"
    output_path = "./MyTTSDataset/metadata_normalized.csv"
    add_normalized_transcription_column(metafile_path, output_path)