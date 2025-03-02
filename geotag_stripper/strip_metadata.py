import os
import argparse
import subprocess

def remove_metadata(image_path):
    """Remove all metadata from an image using exiftool."""
    try:
        # Check if exiftool is installed
        subprocess.run(['exiftool', '-ver'], capture_output=True, text=True)
        
        # Remove all metadata in-place
        result = subprocess.run([
            'exiftool', 
            '-all=', 
            '-overwrite_original', 
            image_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Metadata removed from {image_path}")
        else:
            print(f"Error removing metadata from {image_path}: {result.stderr}")
    
    except FileNotFoundError:
        print("Error: exiftool is not installed. Please install it using: sudo apt-get install libimage-exiftool-perl")
    except Exception as e:
        print(f"Unexpected error processing {image_path}: {e}")

def scan_directory(directory):
    """Recursively scan directory and remove metadata from images."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.webp'}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file.lower())[1] in image_extensions:
                image_path = os.path.join(root, file)
                remove_metadata(image_path)

def main():
    parser = argparse.ArgumentParser(description='Remove metadata from images using exiftool.')
    parser.add_argument('directory', help='Directory to scan')
    
    args = parser.parse_args()
    scan_directory(args.directory)

if __name__ == "__main__":
    main()
