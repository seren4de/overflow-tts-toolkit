#!/usr/bin/env python3
import csv
import logging
import os
import re
from num2words import num2words
from pathlib import Path
from typing import Dict, List, Optional

class TTSDatasetNormalizer:
    """A class to normalize TTS dataset transcriptions by expanding numbers and cleaning file IDs."""
    
    def __init__(self, log_level: int = logging.INFO):
        """Initialize the normalizer with logging configuration."""
        self.logger = self._setup_logging(log_level)
        self.fieldnames = ['ID', 'Transcription', 'Normalized Transcription']
    
    @staticmethod
    def _setup_logging(log_level: int) -> logging.Logger:
        """Set up logging configuration."""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def expand_numbers(self, text: str) -> str:
        """
        Convert all numbers in text to their word representation.
        
        Args:
            text: Input text containing numbers
            
        Returns:
            Text with numbers converted to words
        """
        try:
            # Enhanced pattern to handle more number formats
            pattern = re.compile(r'\b\d+(?:[,.]\d+)*\b')
            
            def convert_match(match):
                try:
                    number = match.group(0)
                    # Remove commas and convert to float
                    clean_number = float(number.replace(',', ''))
                    return num2words(clean_number, lang='en')
                except ValueError as e:
                    self.logger.warning(f"Failed to convert number '{match.group(0)}': {e}")
                    return match.group(0)
            
            return pattern.sub(convert_match, text)
            
        except Exception as e:
            self.logger.error(f"Error expanding numbers in text: {e}")
            return text

    def process_file(self, 
                    input_path: str, 
                    output_path: str, 
                    remove_wav: bool = True,
                    delimiter: str = '|') -> bool:
        """
        Process the input file to normalize transcriptions and optionally remove .wav extensions.
        
        Args:
            input_path: Path to input CSV file
            output_path: Path to output CSV file
            remove_wav: Whether to remove .wav extensions from IDs
            delimiter: CSV delimiter character
            
        Returns:
            bool: True if processing succeeded, False otherwise
        """
        try:
            # Ensure input file exists
            if not os.path.exists(input_path):
                self.logger.error(f"Input file not found: {input_path}")
                return False
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Process the file
            with open(input_path, 'r', encoding='utf-8') as f_in, \
                 open(output_path, 'w', encoding='utf-8', newline='') as f_out:
                
                reader = csv.DictReader(f_in, delimiter=delimiter, fieldnames=self.fieldnames[:2])
                writer = csv.DictWriter(f_out, delimiter=delimiter, fieldnames=self.fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Process each row
                for row in reader:
                    try:
                        # Clean ID if requested
                        if remove_wav:
                            row['ID'] = row['ID'].replace('.wav', '')
                        
                        # Normalize transcription
                        normalized_text = self.expand_numbers(row['Transcription'])
                        
                        # Write the processed row
                        writer.writerow({
                            'ID': row['ID'],
                            'Transcription': row['Transcription'],
                            'Normalized Transcription': normalized_text
                        })
                        
                    except Exception as e:
                        self.logger.error(f"Error processing row {row.get('ID', 'unknown')}: {e}")
                        continue
                        
            self.logger.info(f"Successfully processed {input_path} to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process file: {e}")
            return False

def main():
    """Main entry point for the script."""
    # Configure paths
    base_dir = Path("./MyTTSDataset")
    input_path = base_dir / "metadata.csv"
    intermediate_path = base_dir / "metadata_normalized.csv"
    final_path = base_dir / "metadata_normalized_no_wav.csv"
    
    # Initialize normalizer
    normalizer = TTSDatasetNormalizer()
    
    # Process the file in one pass (combines both original scripts' functionality)
    success = normalizer.process_file(
        input_path=str(input_path),
        output_path=str(final_path),
        remove_wav=True
    )
    
    if not success:
        logging.error("Failed to process the dataset")
        exit(1)

if __name__ == '__main__':
    main()