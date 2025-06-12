"""
Standardize Extracted Data Script

This script standardizes and cleans the extracted equipment data from venue PDFs.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
import re

# Add the schema directory to the path
sys.path.insert(0, str(Path(__file__).parent))
from schema.field_mapping import standardize_field_name, determine_equipment_type, load_schema

def clean_model_name(model_text):
    """Clean and standardize model names."""
    if not model_text or not isinstance(model_text, str):
        return ""
    
    # Remove common prefixes like "Type: ", "Model: ", etc.
    model_text = re.sub(r'^(Type|Model|Name|Description|Item)\s*[:;-]\s*', '', model_text, flags=re.IGNORECASE)
    
    # Remove any trailing punctuation
    model_text = model_text.strip('.,:;-')
    
    # Remove any excessive whitespace
    model_text = re.sub(r'\s+', ' ', model_text).strip()
    
    return model_text

def standardize_quantity(quantity_text):
    """Standardize quantity values."""
    if not quantity_text:
        return ""
    
    # If it's already a number, return it as is
    if isinstance(quantity_text, (int, float)):
        return str(quantity_text)
    
    # Extract numeric value from text
    quantity_text = str(quantity_text)
    match = re.search(r'(\d+)', quantity_text)
    if match:
        return match.group(1)
    
    return quantity_text

def extract_manufacturer(model_text):
    """Try to extract manufacturer from model text."""
    if not model_text or not isinstance(model_text, str):
        return ""
    
    # Common manufacturer patterns
    manufacturers = [
        "ETC", "Martin", "Robe", "Chauvet", "Elation", "Clay Paky", "High End", "Vari-Lite",  # Lighting
        "L-Acoustics", "d&b audiotechnik", "Meyer Sound", "JBL", "Yamaha", "Shure", "Sennheiser", "DPA",  # Sound
        "Christie", "Barco", "Epson", "Sony", "Panasonic", "Samsung", "LG", "NEC"  # Video
    ]
    
    # Check for manufacturer names at the beginning of the model text
    for manufacturer in manufacturers:
        pattern = r'^' + re.escape(manufacturer) + r'\s+'
        if re.search(pattern, model_text, re.IGNORECASE):
            return manufacturer
    
    # Check for other patterns
    patterns = [
        r'^([A-Z][a-zA-Z\s&]+?)\s+[A-Z0-9\-]+',  # Brand followed by model number
        r'([A-Z][a-zA-Z\s&]+)\s+'  # Any capitalized words at the beginning
    ]
    
    for pattern in patterns:
        match = re.search(pattern, model_text)
        if match:
            potential_manufacturer = match.group(1).strip()
            if len(potential_manufacturer) > 2 and len(potential_manufacturer) < 20:
                return potential_manufacturer
    
    return ""

def process_equipment_data(venue_name, equipment_type, csv_path):
    """Process and standardize equipment data from a CSV file."""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        
        # Drop rows with no useful information
        df = df.dropna(subset=['raw_text']).reset_index(drop=True)
        
        # Filter out rows with very short raw_text or page numbers
        df = df[~df['raw_text'].str.match(r'^\s*\d+\s*$', na=False)]
        df = df[df['raw_text'].str.len() > 5].reset_index(drop=True)
        
        # Clean and standardize the data
        standardized_data = []
        
        for _, row in df.iterrows():
            item = {}
            
            # Get the model/equipment name
            if 'model' in row and pd.notna(row['model']) and row['model']:
                item['model'] = clean_model_name(row['model'])
            else:
                # Try to extract model from raw_text
                raw_text = row['raw_text']
                # Skip if raw_text contains too many newlines (likely a section of text, not equipment)
                if raw_text.count('\n') > 5:
                    continue
                
                item['model'] = clean_model_name(raw_text)
            
            # Standardize quantity
            if 'quantity' in row and pd.notna(row['quantity']):
                item['quantity'] = standardize_quantity(row['quantity'])
            else:
                item['quantity'] = ""
            
            # Try to extract manufacturer
            item['manufacturer'] = extract_manufacturer(item['model'])
            if item['manufacturer']:
                # Remove manufacturer from model name to avoid duplication
                item['model'] = re.sub(r'^' + re.escape(item['manufacturer']) + r'\s+', '', item['model'], flags=re.IGNORECASE)
            
            # Add equipment type
            item['equipment_type'] = equipment_type
            
            # Add venue name
            item['venue'] = venue_name
            
            # Add raw text for reference
            item['raw_text'] = row['raw_text'] if 'raw_text' in row and pd.notna(row['raw_text']) else ""
            
            # Add to standardized data if we have a model
            if item['model']:
                standardized_data.append(item)
        
        # Remove duplicates based on model and quantity
        df_standardized = pd.DataFrame(standardized_data)
        if not df_standardized.empty:
            df_standardized = df_standardized.drop_duplicates(subset=['model', 'quantity']).reset_index(drop=True)
        
        return df_standardized
    
    except Exception as e:
        print(f"Error processing {csv_path}: {e}")
        return pd.DataFrame()

def main():
    """Main function to standardize all extracted venue data."""
    # Create output directory
    output_dir = Path(__file__).parent / "output" / "standardized"
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Find all venues with extracted data
    data_dir = Path(__file__).parent / "data"
    venue_dirs = [d for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    if not venue_dirs:
        print("No venue data directories found.")
        return
    
    print(f"Found {len(venue_dirs)} venues with extracted data.")
    
    # Process each venue
    all_equipment = []
    
    for venue_dir in venue_dirs:
        venue_name = venue_dir.name.replace('_', ' ')
        print(f"\nProcessing venue: {venue_name}")
        
        # Look for equipment CSV files
        equipment_files = {
            'lighting': list(venue_dir.glob('*lighting*equipment*.csv')),
            'sound': list(venue_dir.glob('*sound*equipment*.csv')),
            'video': list(venue_dir.glob('*video*equipment*.csv'))
        }
        
        venue_equipment = []
        
        # Process each equipment type
        for eq_type, file_list in equipment_files.items():
            if file_list:
                file_path = file_list[0]  # Take the first matching file
                print(f"Processing {eq_type} equipment from {file_path.name}")
                
                standardized_df = process_equipment_data(venue_name, eq_type, file_path)
                
                if not standardized_df.empty:
                    # Save to CSV
                    output_file = output_dir / f"{venue_name.replace(' ', '_')}_{eq_type}_standardized.csv"
                    standardized_df.to_csv(output_file, index=False)
                    print(f"Saved {len(standardized_df)} standardized {eq_type} items to {output_file}")
                    
                    # Add to venue equipment
                    venue_equipment.extend(standardized_df.to_dict('records'))
        
        # Add to all equipment
        all_equipment.extend(venue_equipment)
        
        # Save combined venue equipment
        if venue_equipment:
            venue_output = output_dir / f"{venue_name.replace(' ', '_')}_all_equipment.csv"
            pd.DataFrame(venue_equipment).to_csv(venue_output, index=False)
            print(f"Saved {len(venue_equipment)} total equipment items for {venue_name}")
    
    # Save all equipment from all venues
    if all_equipment:
        all_output = output_dir / "all_venues_equipment.csv"
        pd.DataFrame(all_equipment).to_csv(all_output, index=False)
        print(f"\nSaved {len(all_equipment)} total equipment items from all venues to {all_output}")
    
    print("\nStandardization complete!")

if __name__ == "__main__":
    main()