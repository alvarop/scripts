#!/usr/bin/env python3
import os
import re
import argparse
import shutil
import datetime
from pathlib import Path

def process_markdown_file(input_file, output_dir, image_output_dir):
    """
    Process a markdown file:
    - Extract title from filename
    - Find and process image tags
    - Copy and rename image files
    - Replace image tags with new format
    - Save the new markdown file
    """
    # Get post title from filename
    base_filename = os.path.basename(input_file)
    post_title = os.path.splitext(base_filename)[0]
    
    # Ensure output directories exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(image_output_dir, exist_ok=True)
    
    # Load the markdown content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the attachments directory (in the same path as the input file)
    input_file_dir = os.path.dirname(input_file)
    attachments_dir = os.path.join(input_file_dir, 'attachments')
    
    # Regular expression to match image tags
    # Format: ![[Pasted image 20250223134448.png|Figure 2-2 from USB-C Spec - Plug Interface]]
    image_pattern = r'!\[\[(.*?)\|(.*?)\]\]'
    
    # Find all image tags
    image_matches = re.findall(image_pattern, content)
    
    # Process each image
    for i, (image_filename, image_description) in enumerate(image_matches, 1):
        # Original image path
        original_image_path = os.path.join(attachments_dir, image_filename.strip())
        
        # Check if the image file exists
        if not os.path.exists(original_image_path):
            print(f"Warning: Image file not found: {original_image_path}")
            continue
        
        # Get file extension
        _, extension = os.path.splitext(image_filename)
        
        # Create new image filename
        new_image_filename = f"{post_title}_{i}{extension}"
        new_image_path = os.path.join(image_output_dir, new_image_filename)
        
        # Copy and rename the image file
        shutil.copy2(original_image_path, new_image_path)
        print(f"Copied {original_image_path} to {new_image_path}")
        
        # Create the replacement image tag
        relative_path = os.path.join(os.path.basename(image_output_dir), new_image_filename)
        replacement = f"""
{{% include image.html 
    img="{relative_path}" 
    title="{image_description.strip()}"
    caption="{image_description.strip()}"
    url="/{relative_path}"
%}}
"""
        
        # Replace the original image tag with the new format
        original_tag = f"![[{image_filename}|{image_description}]]"
        content = content.replace(original_tag, replacement)
    
    # Create the new filename with date prefix
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    new_filename = f"{today}-{base_filename}"
    output_path = os.path.join(output_dir, new_filename)
    
    # Save the modified content to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Processed markdown file saved to: {output_path}")
    
    return output_path

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process markdown files with embedded images")
    parser.add_argument("input_file", help="Input markdown file path")
    parser.add_argument("output_dir", help="Output directory for processed markdown files")
    parser.add_argument("--image-dir", dest="image_output_dir", 
                        help="Output directory for processed images (default: images/)", 
                        default="images")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Process the markdown file
    process_markdown_file(args.input_file, args.output_dir, args.image_output_dir)

if __name__ == "__main__":
    main()
    