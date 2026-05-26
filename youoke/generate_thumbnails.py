import os
import re
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

def extract_video_id(url):
    """
    Extracts the YouTube video ID from various URL formats.
    """
    # Standard watch?v= format
    if 'watch?v=' in url:
        return url.split('watch?v=')[-1].split('&')[0]
    # Short youtu.be format
    elif 'youtu.be/' in url:
        return url.split('youtu.be/')[-1].split('?')[0].split('&')[0]
    # Embed format
    elif '/embed/' in url:
        return url.split('/embed/')[-1].split('?')[0].split('&')[0]
    # Thumbnail URL format itself (just in case)
    elif '/vi/' in url:
        return url.split('/vi/')[-1].split('/')[0]
    
    # Generic regex fallback
    pattern = r'(?:v=|\/vi\/|youtu\.be\/|\/v\/|\/e\/|watch\?v=|\/embed\/|video\/|user\/.*\/|v=)([^#\&\?]*).*'
    match = re.search(pattern, url)
    if match and len(match.group(1)) == 11:
        return match.group(1)
        
    return None

def download_and_resize(video_id, output_path, target_width=200):
    """
    Downloads the YouTube thumbnail and resizes it.
    """
    # Construct thumbnail URL (hqdefault is usually 480x360)
    thumb_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    
    try:
        response = requests.get(thumb_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary (e.g., if it's RGBA)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Calculate new height to maintain aspect ratio
            w_percent = (target_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            
            # Resize using high-quality lanczos filter
            img = img.resize((target_width, h_size), Image.Resampling.LANCZOS)
            
            # Save the image
            img.save(output_path, "JPEG", quality=90)
            return True
        else:
            # Try mqdefault if hqdefault fails
            thumb_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
            response = requests.get(thumb_url, timeout=10)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                w_percent = (target_width / float(img.size[0]))
                h_size = int((float(img.size[1]) * float(w_percent)))
                img = img.resize((target_width, h_size), Image.Resampling.LANCZOS)
                img.save(output_path, "JPEG", quality=90)
                return True
    except Exception as e:
        print(f"  Error processing {video_id}: {e}")
    return False

def main():
    csv_file = 'data.csv'
    output_dir = 'thumbnails'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return

    # Column names for the CSV
    names = ['id', 'singer_en', 'singer_mm', 'song_en', 'song_mm', 'youtube_url']
    
    print(f"Reading {csv_file}...")
    try:
        df = pd.read_csv(csv_file, names=names, header=None)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    total = len(df)
    print(f"Found {total} entries. Starting processing...")
    
    count = 0
    for index, row in df.iterrows():
        song_id = str(row['id']).strip()
        url = str(row['youtube_url']).strip()
        
        # Skip empty URLs
        if not url or url == 'nan':
            continue
            
        video_id = extract_video_id(url)
        if video_id:
            output_path = os.path.join(output_dir, f"{song_id}.jpg")
            
            # Check if file already exists to skip (optional)
            # if os.path.exists(output_path):
            #     continue
                
            if download_and_resize(video_id, output_path):
                count += 1
                if count % 10 == 0 or count == total:
                    print(f"  Processed {count}/{total} thumbnails...")
            else:
                print(f"  [!] Failed for ID {song_id} (URL: {url})")
        else:
            print(f"  [!] Could not extract ID from: {url}")

    print(f"\nFinished! Total thumbnails generated: {count}")

if __name__ == "__main__":
    main()
