# Fine-Tuned TTS Overflow Model

A repository containing a fine-tuned Text-to-Speech (TTS) overflow model for single-speaker voice synthesis, optimized for audiobook narration.

## Prerequisites

- Python 3.8+
- CUDA-compatible GPU
- Two separate virtual environments for:
  - [Montreal Forced Aligner (MFA)](https://montreal-forced-aligner.readthedocs.io/en/latest/getting_started.html)
  - [TTS](https://tts.readthedocs.io/en/latest/inference.html)

## Project Structure

```bash
.
├── audio/                      # Audio processing directory
│   ├── input_audio/           # Raw audio files
│   └── output_audio/          # Processed WAV files
├── corpus_directory/          # Aligned audio-text data
│   └── Speaker1/             # Single speaker data
├── MyTTSDataset/             # Training dataset
│   ├── metadata.csv
│   └── wavs/
├── out/                      # Training outputs
│   ├── 1e-3/                # Learning rate experiments
│   ├── 1e-4/
│   ├── 1e-5/
│   └── phoneme_cache/
└── text/                     # Text processing
    ├── input_text/
    └── output_text/
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
python3 mp32wav_.py ./audio/input_audio/chapters/unfollow/ ./audio/output_audio/unfollow/
mv ./audio/output_audio/unfollow/* ./corpus_directory/Speaker1/
```

2. **Process EPub Books**:
```bash
python3 splitepub_.py ./text/input_text/Unfollow.epub ./text/input_text/
```

3. **Tokenize Text**:
```bash
python3 tokenize_.py
```

4. **Split into Sentences**:
```bash
python3 split2sentences_.py ./corpus_directory/
```

### 3. Audio-Text Alignment

Option 1: Using alignaudiotext_.py
```bash
python3 alignaudiotext_.py
# Note: Press Enter in terminal to update if process appears frozen
```

Option 2: Using MFA directly
```bash
mfa align --clean --single_speaker './corpus_directory' 'english_us_arpa' 'english_us_arpa' './corpus_directory'
```

### 4. Training the Model

Clean and prepare training data:
```bash
(tts) ┌──(seren4de㉿Bitland)-[~/overflow_ft]
└─$ python clean_.py
└─$ python rmextmeta_py
```

Start training with one of these configurations:

```bash
# Basic configuration
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:25' python train_overflow.py \
    --config_path ./config.json \
    --restore_path $HOME/.local/share/tts/tts_models--en--ljspeech--overflow/model_file.pth

# Alternative configuration (21MB split size)
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:21' python train_overflow.py \
    --config_path /home/seren4de/overflow_ft/config.json \
    --restore_path /home/seren4de/.local/share/tts/tts_models--en--ljspeech--overflow/model_file.pth

# Continue training from checkpoint
CUDA_VISIBLE_DEVICES="0" PYTORCH_CUDA_ALLOC_CONF='max_split_size_mb:21' python train_overflow.py \
    --config_path /home/seren4de/overflow_ft/out/1e-5/config.json \
    --restore_path /home/seren4de/overflow_ft/out/1e-5/checkpoint_21500.pth
```

## Project Files

- `alignaudiotext_.py`: Aligns audio with transcripts
- `clean_.py`: Preprocesses training data
- `format.py`: Formats text data
- `mp32wav_.py`: Converts MP3 to WAV
- `rmextmeta_py`: Removes external metadata
- `split2sentences_.py`: Splits text into sentences
- `splitepub_.py`: Extracts text from EPUB files
- `tokenize_.py`: Tokenizes text data
- `train_overflow.py`: Main training script

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
