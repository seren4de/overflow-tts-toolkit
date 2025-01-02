import os
import sys
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def split_epub_to_chapters(epub_path, output_dir):
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the EPUB file using ebooklib
    book = epub.read_epub(epub_path)

    # Iterate over the items in the EPUB file
    for item in book.get_items():
        # Check if the item is an XHTML document (i.e., a chapter)
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            # Extract the chapter title from the item's file name
            chapter_title = os.path.splitext(item.get_name())[0]
            # Construct the full path to the output text file for this chapter
            text_path = os.path.join(output_dir, f'{chapter_title}.txt')
            # Create any missing subdirectories in the output directory
            os.makedirs(os.path.dirname(text_path), exist_ok=True)
            # Parse the item's content using BeautifulSoup
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            # Extract the text from the item's content
            text = soup.get_text()
            # Save the text to the output text file
            with open(text_path, 'w') as f:
                f.write(text)

if __name__ == '__main__':
    # Parse the command-line arguments
    epub_path = sys.argv[1]
    output_dir = sys.argv[2]
    # Split the EPUB book into chapters
    split_epub_to_chapters(epub_path, output_dir)