import os
import subprocess
from pydub import AudioSegment
from pydub.silence import split_on_silence

def start_new_mfa_server():
    start = 'mfa server start'
    delete = 'mfa server delete'
    init = 'mfa server init'
    subprocess.run(start, shell=True)
    subprocess.run(delete, shell=True)
    subprocess.run(init, shell=True)


def align_audio():
    corpus_directory = './corpus_directory'
    dictionary_path = 'english_us_arpa'
    acoustic_model_path = 'english_us_arpa'
    output_directory =  corpus_directory

    mfa_command = f'mfa align --clean --single_speaker {corpus_directory} {dictionary_path} {acoustic_model_path} {output_directory}'
    subprocess.run(mfa_command, shell=True)

if __name__ == '__main__':
    print(f'[+] starting a new mfa server ::')
    start_new_mfa_server()
    print(f'[+] aligning audio ::')
    align_audio() 