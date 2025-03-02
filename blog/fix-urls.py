#!/usr/bin/env python3
import os
import re
import sys
import argparse
import urllib.parse
from pathlib import Path

def encode_image_urls(directory_path):
    """
    Process all markdown files in the given directory to URL encode spaces
    in image URLs.
    """
    # Ensure the directory exists
    if not os.path.isdir(directory_path):
        print(f"Error: Directory '{directory_path}' does not exist.")
        return False
    
    # Find all markdown files in the directory
    md_files = list(Path(directory_path).glob('*.md'))
    print(f"Found {len(md_files)} markdown files.")
    
    # Counter for modified files
    modified_count = 0
    total_replacements = 0
    
    # Regular expression to match markdown image syntax
    # Captures: ![alt text](/path/with spaces/image.jpg)
    image_pattern = r'!\[(.*?)\]\((.*?)\)'
    
    # Process each markdown file
    for md_file in md_files:
        filename = md_file.name
        file_replacements = 0
        
        # Read file content
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Find all image tags
        def encode_url(match):
            nonlocal file_replacements
            alt_text = match.group(1)
            url = match.group(2)
            
            # Check if URL contains spaces
            if ' ' in url:
                # Split the URL to preserve any potential query parameters or fragment identifiers
                url_parts = url.split('?', 1)
                path = url_parts[0]
                query = f"?{url_parts[1]}" if len(url_parts) > 1 else ""
                
                # Encode spaces in the path part
                encoded_path = path.replace(' ', '%20')
                encoded_url = encoded_path + query
                
                file_replacements += 1
                return f'![{alt_text}]({encoded_url})'
            else:
                return match.group(0)
        
        # Replace image URLs with encoded versions
        new_content = re.sub(image_pattern, encode_url, content)
        
        # If changes were made, write back to file
        if file_replacements > 0:
            with open(md_file, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print(f"Updated {filename}: Encoded {file_replacements} image URLs")
            modified_count += 1
            total_replacements += file_replacements
        else:
            print(f"Skipping {filename}: No image URLs with spaces found.")
    
    print(f"\nOperation complete: {modified_count} files were modified with {total_replacements} total URL encodings.")
    return True

def main():
    parser = argparse.ArgumentParser(description="URL encode spaces in markdown image URLs.")
    parser.add_argument("directory", help="Directory containing markdown files to process")
    
    args = parser.parse_args()
    
    if not encode_image_urls(args.directory):
        sys.exit(1)

if __name__ == "__main__":
    main()