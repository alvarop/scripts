#!/usr/bin/env python3
import os
import re
import sys
import argparse
from pathlib import Path

def add_date_to_frontmatter(directory_path):
    """
    Process all markdown files in the given directory to add a date field
    to the YAML front matter based on the date in the filename.
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
    
    # Process each markdown file
    for md_file in md_files:
        filename = md_file.name
        
        # Extract date from filename (YYYY-MM-DD-title.md)
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})-(.*?)\.md', filename)
        if not date_match:
            print(f"Skipping {filename}: Could not extract date from filename.")
            continue
        
        date = date_match.group(1)
        
        # Read file content
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file has YAML front matter
        frontmatter_match = re.match(r'^---\s+(.*?)\s+---', content, re.DOTALL)
        if not frontmatter_match:
            print(f"Skipping {filename}: No YAML front matter found.")
            continue
        
        frontmatter = frontmatter_match.group(1)
        
        # Check if date field already exists
        if re.search(r'^date:', frontmatter, re.MULTILINE):
            print(f"Skipping {filename}: Date field already exists.")
            continue
        
        # Determine where to insert the date line
        lines = frontmatter.split('\n')
        title_index = next((i for i, line in enumerate(lines) if line.startswith('title:')), -1)
        
        if title_index >= 0:
            # Insert after title line
            insert_index = title_index + 1
            lines.insert(insert_index, f"date: {date}")
        else:
            # Insert at the beginning
            lines.insert(0, f"date: {date}")
        
        # Reconstruct the front matter
        new_frontmatter = '\n'.join(lines)
        new_content = content.replace(frontmatter, new_frontmatter)
        
        # Write the modified content back to the file
        with open(md_file, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Updated {filename} with date: {date}")
        modified_count += 1
    
    print(f"\nOperation complete: {modified_count} files were modified.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Add date to markdown front matter based on filename.")
    parser.add_argument("directory", help="Directory containing markdown files to process")
    
    args = parser.parse_args()
    
    if not add_date_to_frontmatter(args.directory):
        sys.exit(1)

if __name__ == "__main__":
    main()