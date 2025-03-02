#!/usr/bin/env python3
import os
import re
import sys
import argparse
from pathlib import Path

def convert_categories_to_tags(directory_path):
    """
    Process all markdown files in the given directory to:
    1. Move any categories into the tags section
    2. Remove the categories section entirely
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
        
        # Read file content
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Check if file has YAML front matter
        frontmatter_match = re.match(r'^---\s+(.*?)\s+---', content, re.DOTALL)
        if not frontmatter_match:
            print(f"Skipping {filename}: No YAML front matter found.")
            continue
        
        frontmatter_text = frontmatter_match.group(1)
        
        # Check if categories exist
        if 'categories:' not in frontmatter_text:
            print(f"Skipping {filename}: No categories section found.")
            continue
        
        # Parse the frontmatter manually to handle multiline YAML properly
        frontmatter_lines = frontmatter_text.split('\n')
        
        # Extract categories
        categories = []
        in_categories_section = False
        categories_indices = []
        
        for i, line in enumerate(frontmatter_lines):
            if line.strip() == 'categories:':
                in_categories_section = True
                categories_indices.append(i)
            elif in_categories_section and line.strip().startswith('- '):
                categories.append(line.strip()[2:])  # Remove the '- ' prefix
                categories_indices.append(i)
            elif in_categories_section and (line.strip() and not line.strip().startswith('- ')):
                in_categories_section = False
        
        if not categories:
            print(f"Skipping {filename}: Categories section exists but contains no items.")
            continue
        
        # Create a new frontmatter with the changes
        new_frontmatter_lines = frontmatter_lines.copy()
        
        # Remove categories section (from last index to first to avoid index shifting)
        for i in sorted(categories_indices, reverse=True):
            new_frontmatter_lines.pop(i)
        
        # Find tags section or determine where to add it
        has_tags_section = False
        tags_empty_array = False
        tags_line_index = -1
        
        for i, line in enumerate(new_frontmatter_lines):
            if line.strip() == 'tags: []':
                has_tags_section = True
                tags_empty_array = True
                tags_line_index = i
                break
            elif line.strip() == 'tags:':
                has_tags_section = True
                tags_line_index = i
                break
        
        # Handle tags section
        if has_tags_section:
            if tags_empty_array:
                # Replace 'tags: []' with expanded format
                new_frontmatter_lines[tags_line_index] = 'tags:'
                for category in reversed(categories):
                    new_frontmatter_lines.insert(tags_line_index + 1, f'- {category}')
            else:
                # Add categories to existing tags
                for category in reversed(categories):
                    new_frontmatter_lines.insert(tags_line_index + 1, f'- {category}')
        else:
            # Add new tags section at the end
            new_frontmatter_lines.append('tags:')
            for category in categories:
                new_frontmatter_lines.append(f'- {category}')
        
        # Reconstruct the front matter
        new_frontmatter = '\n'.join(new_frontmatter_lines)
        new_content = content.replace(frontmatter_text, new_frontmatter)
        
        # Write the modified content back to the file
        with open(md_file, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Updated {filename}: Moved {len(categories)} categories to tags")
        modified_count += 1
    
    print(f"\nOperation complete: {modified_count} files were modified.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Convert categories to tags in markdown files.")
    parser.add_argument("directory", help="Directory containing markdown files to process")
    
    args = parser.parse_args()
    
    if not convert_categories_to_tags(args.directory):
        sys.exit(1)

if __name__ == "__main__":
    main()