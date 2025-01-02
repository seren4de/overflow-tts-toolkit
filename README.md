# Fine-Tuned TTS Overflow Model

A ProofOfConcept for fine-tuning the overflow TTS (Text To Speech) model for single-speaker voice synthesis, optimized for audiobook narration.

## Prerequisites

- Python 3.8+
- CUDA-compatible GPU
- Two separate virtual environments for:
  - [Montreal Forced Aligner (MFA)](https://montreal-forced-aligner.readthedocs.io/en/latest/getting_started.html)
  - [TTS](https://tts.readthedocs.io/en/latest/inference.html)

## Project Structure

```bash
.
├── audio/                    # Audio processing directory
│   ├── input/                # Raw audio files
│   └── output/               # Processed WAV files
├── corpus_directory/         # Aligned audio-text data
│   └── Speaker1/             # Single speaker data
├── MyTTSDataset/             # Training dataset
│   ├── metadata.csv
│   └── wavs/
├── ls/                      # Training outputs
│   ├── 1e-3/                # Learning rate experiments
│   ├── 1e-4/
│   ├── 1e-5/
│   └── phoneme_cache/
└── text/                    # Text processing
    ├── input/
    └── output/
```

## Setup Instructions

### 1. MFA Environment Setup

```bash
# Activate MFA environment
conda activate aligner

# Update Montreal Forced Aligner
conda update montreal-forced-aligner

# Initialize MFA server
mfa server start
mfa server delete
mfa server init
```

### 2. Data Preparation

1. **Convert MP3 to WAV**:
```bash
python3 mp3Towav.py <audio/input> ./corpus_directory/Speaker1/
```

2. **Process EPub Books to sentences and tokenize them**:
```bash
python splitEpubToSentences.py input.epub ./work_dir ./output_dir
```

3. **Split speech to Sentences**:
```bash
python3 speechDatasetPreprocessor.py ./corpus_directory/
```

### 3. Audio-Text Alignment

Option 1: Using the wrapper script [`alignSpeechToText.py`](./alignSpeechToText.py)
```bash
python3 alignSpeechToText.py
# Note: Press Enter in terminal to update if process appears frozen
```

Option 2: Using MFA directly
```bash
mfa align --clean --single_speaker './corpus_directory' 'english_us_arpa' 'english_us_arpa' './corpus_directory'
```

### 4. Training the Model

Clean and prepare training data:
```bash
(tts) [/tmp/overflow-tts-toolkit]
$ python TTSDatasetNormalizer.py
```

Start training with one of these configurations:

```bash
# Basic configuration
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:25' python trainOverflow.py \
    --config_path ./config.json \
    --restore_path $HOME/.local/share/tts/tts_models--en--ljspeech--overflow/model_file.pth

# Alternative configuration (21MB split size)
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:21' python trainOverflow.py \
    --config_path /tmp/overflow-tts-toolkit/config.json \
    --restore_path $HOME/.local/share/tts/tts_models--en--ljspeech--overflow/model_file.pth

# Continue training from checkpoint
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:21' python trainOverflow.py \
    --config_path /tmp/overflow-tts-toolkit/lr/1e-5/config.json \
    --restore_path $HOME/overflow_ft/lr/1e-5/checkpoint_21500.pth
```

## Project Files

- [`alignSpeechToText.py`](./alignSpeechToText.py): Aligns audio/speech with transcript
- [`TTSDatasetNormalizer.py`](./TTSDatasetNormalizer.py): Preprocesses training data and removes external metadata
- [`format.py`](./format.py): Formats text data
- [`mp3Towav.py`](./mp3Towav.py): Converts MP3 to WAV
- [`speechDatasetPreprocessor.py`](./speechDatasetPreprocessor.py): Splits speech to Sentences
- [`splitEpubToSentences.py`](./splitEpubToSentences.py): Extracts and splits text from EPUB to txt sentences
- [`trainOverflow.py`](./trainOverflow.py): Main training script

## Dataset Structure

The corpus directory should follow this structure:
```bash
corpus_directory/
└── Speaker1/
    ├── Unfollow_01.txt
    ├── Unfollow_01.wav
    ├── Unfollow_01.TextGrid
    └── ...
```

## Notes

- All paths should be adjusted according to your system setup
- GPU memory requirements may vary based on your hardware
- For optimal results, ensure high-quality audio input files
