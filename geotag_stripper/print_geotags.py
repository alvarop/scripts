import os
import sys
import argparse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def convert_gps_coordinates(coordinates, ref):
    """Convert GPS coordinates to decimal degrees."""
    degrees, minutes, seconds = coordinates
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def get_geotagging(exif):
    """Extract GPS information from EXIF data."""
    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                return None
            
            gps_data = exif[idx]
            for (key, val) in GPSTAGS.items():
                if key in gps_data:
                    geotagging[val] = gps_data[key]
    
    # Convert coordinates to decimal degrees and generate Maps URL
    if all(k in geotagging for k in ['GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef']):
        lat = convert_gps_coordinates(geotagging['GPSLatitude'], geotagging['GPSLatitudeRef'])
        lon = convert_gps_coordinates(geotagging['GPSLongitude'], geotagging['GPSLongitudeRef'])
        geotagging['DecimalLatitude'] = lat
        geotagging['DecimalLongitude'] = lon
        geotagging['GoogleMapsURL'] = f"https://www.google.com/maps?q={lat},{lon}"
    
    return geotagging

def scan_directory(directory, strip=False):
    """Scan directory recursively for images with geotag info."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.webp'}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file.lower())[1] in image_extensions:
                image_path = os.path.join(root, file)
                
                try:
                    image = Image.open(image_path)
                    exif = image._getexif()
                    
                    if exif:
                        geotagging = get_geotagging(exif)
                        
                        if geotagging and 'GoogleMapsURL' in geotagging:
                            print(f"Geotag found in {image_path}:")
                            for tag, value in geotagging.items():
                                print(f"  {tag}: {value}")
                
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Scan images for geotag information.')
    parser.add_argument('directory', help='Directory to scan')
    
    args = parser.parse_args()
    scan_directory(args.directory)

if __name__ == "__main__":
    main()