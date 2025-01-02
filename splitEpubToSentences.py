#!/usr/bin/env python3
import os
import sys
import logging
from typing import List, Optional, Tuple, Generator
from pathlib import Path

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

class EPUBTranscriptProcessor:
    """Process EPUB files into speaker-attributed transcripts with sentence tokenization."""
    
    def __init__(self, download_nltk: bool = True, log_level: int = logging.INFO):
        """
        Initialize the processor.
        
        Args:
            download_nltk: Whether to download required NLTK data
            log_level: Logging level to use
        """
        self.logger = self._setup_logging(log_level)
        if download_nltk:
            self._ensure_nltk_data()
    
    @staticmethod
    def _setup_logging(log_level: int) -> logging.Logger:
        """Configure logging."""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    @staticmethod
    def _ensure_nltk_data():
        """Download required NLTK data if not present."""
        try:
            nltk.download('punkt', quiet=True)
        except Exception as e:
            logging.warning(f"Failed to download NLTK data: {e}")
            logging.warning("Sentence tokenization might not work correctly.")
    
    def extract_chapters(self, epub_path: str, output_dir: str) -> List[str]:
        """
        Extract chapters from EPUB file into separate text files.
        
        Args:
            epub_path: Path to input EPUB file
            output_dir: Directory to save extracted chapter files
            
        Returns:
            List of paths to extracted chapter files
        """
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            chapter_files = []
            
            # Load and process EPUB
            book = epub.read_epub(epub_path)
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    try:
                        # Extract chapter info
                        chapter_title = os.path.splitext(item.get_name())[0]
                        text_path = os.path.join(output_dir, f'{chapter_title}.txt')
                        os.makedirs(os.path.dirname(text_path), exist_ok=True)
                        
                        # Process chapter content
                        soup = BeautifulSoup(item.get_content(), 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        
                        # Save chapter
                        with open(text_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        
                        chapter_files.append(text_path)
                        self.logger.info(f"Extracted chapter: {chapter_title}")
                        
                    except Exception as e:
                        self.logger.error(f"Error processing chapter {item.get_name()}: {e}")
                        continue
            
            return chapter_files
            
        except Exception as e:
            self.logger.error(f"Failed to process EPUB {epub_path}: {e}")
            return []
    
    def process_transcript(self, 
                         input_file: str,
                         output_file: str,
                         default_speaker: str,
                         encoding: str = 'utf-8') -> bool:
        """
        Process a text file into speaker-attributed sentences.
        
        Args:
            input_file: Path to input text file
            output_file: Path to output transcript file
            default_speaker: Default speaker name for unattributed text
            encoding: File encoding to use
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(input_file, 'r', encoding=encoding) as f_in, \
                 open(output_file, 'w', encoding=encoding) as f_out:
                
                for line in f_in:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Extract speaker if present, otherwise use default
                    if '\t' in line:
                        speaker, text = line.split('\t', 1)
                    else:
                        speaker = default_speaker
                        text = line
                    
                    # Tokenize and write sentences
                    for sentence in sent_tokenize(text):
                        sentence = sentence.strip()
                        if sentence:
                            f_out.write(f'{speaker}\t{sentence}\n')
            
            self.logger.info(f"Processed transcript: {input_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process transcript {input_file}: {e}")
            return False
    
    def process_epub_to_transcripts(self,
                                  epub_path: str,
                                  work_dir: str,
                                  output_dir: str,
                                  default_speaker: str = "Speaker1") -> bool:
        """
        Process an EPUB file into speaker-attributed transcripts.
        
        Args:
            epub_path: Path to input EPUB file
            work_dir: Directory for intermediate files
            output_dir: Directory for final transcript files
            default_speaker: Default speaker name for unattributed text
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Extract chapters
            chapter_dir = os.path.join(work_dir, 'chapters')
            chapter_files = self.extract_chapters(epub_path, chapter_dir)
            
            if not chapter_files:
                self.logger.error("No chapters extracted from EPUB")
                return False
            
            # Process each chapter into a transcript
            os.makedirs(output_dir, exist_ok=True)
            success_count = 0
            
            for chapter_file in chapter_files:
                output_file = os.path.join(
                    output_dir,
                    os.path.basename(chapter_file)
                )
                
                if self.process_transcript(
                    chapter_file,
                    output_file,
                    default_speaker
                ):
                    success_count += 1
            
            self.logger.info(
                f"Processed {success_count}/{len(chapter_files)} chapters successfully"
            )
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to process EPUB to transcripts: {e}")
            return False

def main():
    """Command-line interface for the processor."""
    if len(sys.argv) != 4:
        print("Usage: script.py <epub_file> <work_dir> <output_dir>")
        sys.exit(1)
    
    epub_path = sys.argv[1]
    work_dir = sys.argv[2]
    output_dir = sys.argv[3]
    
    processor = EPUBTranscriptProcessor()
    success = processor.process_epub_to_transcripts(
        epub_path=epub_path,
        work_dir=work_dir,
        output_dir=output_dir
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()