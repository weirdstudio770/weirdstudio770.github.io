import pandas as pd
import json

def convert_csv_to_json():
    csv_file = 'data.csv'
    json_file = 'data.json'
    
    # Column names based on the data structure seen in generate_thumbnails.py
    names = ['id', 'singer_en', 'singer_mm', 'song_en', 'song_mm', 'youtube_url']
    
    print(f"Reading {csv_file}...")
    try:
        # Read CSV without header, assigning our own column names
        df = pd.read_csv(csv_file, names=names, header=None)
        
        # Clean up any potential whitespace in string columns
        for col in names:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        
        # Convert to a list of dictionaries
        data = df.to_dict(orient='records')
        
        # Save to JSON file
        print(f"Saving to {json_file}...")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully converted {len(data)} entries to {json_file}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert_csv_to_json()