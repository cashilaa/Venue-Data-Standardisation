"""
Improved Final Output Script

This script processes the standardized equipment data and creates a clean, final output
focusing on the actual equipment items for each venue, addressing specific data quality issues.
"""

import os
import sys
import json
import re
import pandas as pd
from pathlib import Path

def is_valid_equipment(model_text, manufacturer_text):
    """Check if the model and manufacturer represent valid equipment."""
    if not model_text or pd.isna(model_text):
        return False
        
    # Check for common page markers or irrelevant content
    invalid_patterns = [
        r'^Page\s+\d+',                   # Page numbers
        r'^Technical\s+and',              # Document headings
        r'^Contents',                      # Table of contents
        r'^Introduction',                  # Section headings
        r'^\d+\.\d+',                      # Section numbers
        r'^[A-Z][a-z]+ \d+, \d{4}',        # Dates
        r'^The\s+',                        # Sentences starting with "The"
        r'^[Aa]nd\s+',                     # Sentences starting with "and"
        r'^[Ii]n\s+',                      # Sentences starting with "in"
        r'^[Ww]ith\s+',                    # Sentences starting with "with"
        r'^[Ff]or\s+',                     # Sentences starting with "for"
        r'\s+the\s+',                      # Sentences containing "the"
    ]
    
    # Check for invalid patterns
    for pattern in invalid_patterns:
        if re.search(pattern, model_text, re.IGNORECASE):
            return False
    
    # Check for model text that's too long or too short
    if len(model_text) > 50 or len(model_text) < 2:
        return False
    
    # Check for model text that contains too many words
    if len(model_text.split()) > 6:
        return False
    
    return True

def clean_model_text(model_text):
    """Clean and standardize model text."""
    if not model_text or pd.isna(model_text):
        return ""
    
    # Remove line breaks, extra spaces
    model_text = re.sub(r'\s+', ' ', model_text).strip()
    
    # Remove common prefixes
    model_text = re.sub(r'^(Type|Model|Name|Description|Item)\s*[:;-]\s*', '', model_text, flags=re.IGNORECASE)
    
    # Remove any trailing punctuation
    model_text = re.sub(r'[.,;:"\'-]+$', '', model_text).strip()
    
    # Remove any numbers at the beginning that are likely not part of the model name
    model_text = re.sub(r'^\d+\s+', '', model_text)
    
    return model_text

def identify_manufacturer(text, common_manufacturers):
    """Try to identify manufacturer from text."""
    if not text or pd.isna(text):
        return ""
    
    # Check if text starts with a known manufacturer
    for manufacturer in common_manufacturers:
        pattern = r'^' + re.escape(manufacturer) + r'\s+'
        if re.search(pattern, text, re.IGNORECASE):
            # Extract the manufacturer and return it with proper capitalization
            match = re.search(pattern, text, re.IGNORECASE)
            return text[:match.end()].strip()
    
    # Try to extract potential manufacturer using pattern matching
    # Look for capitalized words at the beginning
    match = re.match(r'^([A-Z][a-zA-Z\s&]+?)\s+', text)
    if match:
        potential_manufacturer = match.group(1).strip()
        # Only consider it a manufacturer if it's a reasonable length
        if 2 < len(potential_manufacturer) < 20:
            return potential_manufacturer
    
    return ""

def extract_model_info(text, common_manufacturers):
    """Extract manufacturer and model from text."""
    manufacturer = identify_manufacturer(text, common_manufacturers)
    
    if manufacturer:
        # Remove manufacturer from the beginning of the text to get the model
        model = re.sub(r'^' + re.escape(manufacturer) + r'\s+', '', text, flags=re.IGNORECASE)
        return manufacturer, model
    
    # If no manufacturer identified, the whole text is the model
    return "", text

def clean_equipment_data(df):
    """Clean and standardize equipment data."""
    # Define common manufacturers by equipment type
    common_manufacturers = {
        'lighting': [
            'ETC', 'Martin', 'Robe', 'Chauvet', 'Elation', 'Clay Paky', 'High End', 
            'Vari-Lite', 'Robert Juliat', 'Philips', 'GLP', 'Ayrton', 'SGM', 'MA Lighting'
        ],
        'sound': [
            'Shure', 'Sennheiser', 'Audio-Technica', 'AKG', 'DPA', 'Yamaha', 'DiGiCo', 
            'Allen & Heath', 'Midas', 'Behringer', 'L-Acoustics', 'd&b audiotechnik', 
            'Meyer Sound', 'JBL', 'QSC', 'Bose', 'Neumann', 'Beyerdynamic', 'SSL'
        ],
        'video': [
            'Christie', 'Barco', 'Epson', 'Sony', 'Panasonic', 'Samsung', 'LG', 'NEC', 
            'Blackmagic Design', 'Roland', 'Extron', 'Kramer', 'AJA', 'Crestron'
        ]
    }
    
    # Flatten the manufacturer list for easier lookup
    all_manufacturers = [m for sublist in common_manufacturers.values() for m in sublist]
    
    # Create empty result dataframe
    result_data = []
    
    # Process each row
    for _, row in df.iterrows():
        model_text = row['model'] if 'model' in row and pd.notna(row['model']) else ""
        manufacturer_text = row['manufacturer'] if 'manufacturer' in row and pd.notna(row['manufacturer']) else ""
        equipment_type = row['equipment_type'] if 'equipment_type' in row else ""
        venue = row['venue'] if 'venue' in row else ""
        quantity = row['quantity'] if 'quantity' in row and pd.notna(row['quantity']) else ""
        
        # Clean model text
        model_text = clean_model_text(model_text)
        
        # Skip invalid equipment
        if not is_valid_equipment(model_text, manufacturer_text):
            continue
        
        # If manufacturer is empty, try to extract it from model
        if not manufacturer_text:
            type_manufacturers = common_manufacturers.get(equipment_type, all_manufacturers)
            manufacturer_text, model_text = extract_model_info(model_text, type_manufacturers)
        
        # Add cleaned data to results
        result_data.append({
            'manufacturer': manufacturer_text,
            'model': model_text,
            'quantity': quantity,
            'equipment_type': equipment_type,
            'venue': venue
        })
    
    # Convert to DataFrame
    result_df = pd.DataFrame(result_data)
    
    # Remove duplicates based on manufacturer, model, and equipment_type
    result_df = result_df.drop_duplicates(subset=['manufacturer', 'model', 'equipment_type']).reset_index(drop=True)
    
    # Filter out rows with empty model (we want at least manufacturer or model)
    result_df = result_df[result_df['model'].str.strip() != ""].reset_index(drop=True)
    
    return result_df

def extract_specific_equipment(raw_text, equipment_type, venue):
    """Extract specific equipment from raw text."""
    equipment_data = []
    
    # Common equipment patterns
    patterns = [
        # Quantity + Manufacturer + Model
        r'(\d+)\s+([A-Z][a-zA-Z\s&]+)\s+([A-Za-z0-9\-\s]+)',
        
        # Manufacturer + Model + Quantity
        r'([A-Z][a-zA-Z\s&]+)\s+([A-Za-z0-9\-\s]+)\s+(\d+)',
        
        # Manufacturer + Model
        r'([A-Z][a-zA-Z\s&]+)\s+([A-Za-z0-9\-\s]+)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, raw_text)
        for match in matches:
            parts = match.groups()
            
            if len(parts) == 3:  # Pattern with quantity
                # Determine if quantity is first or last
                if parts[0].isdigit():
                    quantity = parts[0]
                    manufacturer = parts[1]
                    model = parts[2]
                else:
                    manufacturer = parts[0]
                    model = parts[1]
                    quantity = parts[2]
            else:  # Pattern without quantity
                manufacturer = parts[0]
                model = parts[1]
                quantity = ""
            
            # Clean the extracted data
            manufacturer = manufacturer.strip()
            model = model.strip()
            
            # Add to results
            equipment_data.append({
                'manufacturer': manufacturer,
                'model': model,
                'quantity': quantity,
                'equipment_type': equipment_type,
                'venue': venue
            })
    
    return equipment_data

def main():
    """Main function to create improved final output."""
    # Find standardized data
    standardized_dir = Path(__file__).parent / "output" / "standardized"
    if not standardized_dir.exists():
        print("Standardized data directory not found.")
        return
    
    # Create final output directory
    final_dir = Path(__file__).parent / "output" / "final"
    final_dir.mkdir(exist_ok=True, parents=True)
    
    # Find all venue files
    venue_files = list(standardized_dir.glob("*_all_equipment.csv"))
    
    if not venue_files:
        print("No venue equipment files found.")
        return
    
    print(f"Found {len(venue_files)} venue equipment files.")
    
    # Process each venue's data
    all_final_data = []
    
    for venue_file in venue_files:
        venue_name = venue_file.name.replace('_all_equipment.csv', '')
        print(f"\nProcessing venue: {venue_name}")
        
        try:
            # Read the data
            df = pd.read_csv(venue_file)
            
            # Clean the data
            cleaned_df = clean_equipment_data(df)
            
            # Save the final output
            output_file = final_dir / f"{venue_name}_final.csv"
            cleaned_df.to_csv(output_file, index=False)
            print(f"Saved {len(cleaned_df)} cleaned equipment items to {output_file}")
            
            # Create separate files for each equipment type
            for eq_type in ['lighting', 'sound', 'video']:
                type_df = cleaned_df[cleaned_df['equipment_type'] == eq_type]
                if not type_df.empty:
                    type_file = final_dir / f"{venue_name}_{eq_type}_final.csv"
                    type_df.to_csv(type_file, index=False)
                    print(f"  - {eq_type.capitalize()}: {len(type_df)} items")
            
            # Add to combined data
            all_final_data.append(cleaned_df)
        
        except Exception as e:
            print(f"Error processing {venue_file}: {e}")
    
    # Combine all final data
    if all_final_data:
        combined_df = pd.concat(all_final_data)
        combined_df = combined_df.drop_duplicates(subset=['manufacturer', 'model', 'equipment_type']).reset_index(drop=True)
        combined_file = final_dir / "all_venues_final.csv"
        combined_df.to_csv(combined_file, index=False)
        print(f"\nSaved {len(combined_df)} total unique equipment items from all venues to {combined_file}")
    
    print("\nFinal data processing complete!")

if __name__ == "__main__":
    main()