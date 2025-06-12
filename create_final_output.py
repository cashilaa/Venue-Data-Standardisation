"""
Create Final Output Script

This script processes the standardized equipment data and creates a clean, final output
focusing on the actual equipment items for each venue.
"""

import os
import sys
import json
import re
import pandas as pd
from pathlib import Path

def clean_equipment_data(df):
    """Clean the standardized equipment data to focus on actual equipment items."""
    # Drop rows with very long model text (likely not equipment)
    df = df[df['model'].str.len() < 100].reset_index(drop=True)
    
    # Drop rows with page numbers or common non-equipment patterns
    df = df[~df['model'].str.match(r'^Page\s+\d+.*', na=False)].reset_index(drop=True)
    df = df[~df['model'].str.match(r'^Technical and.*', na=False)].reset_index(drop=True)
    df = df[~df['model'].str.match(r'^Contents.*', na=False)].reset_index(drop=True)
    
    # Extract more specific equipment based on patterns
    equipment_items = []
    
    for _, row in df.iterrows():
        # Skip rows without model information
        if not row['model'] or pd.isna(row['model']):
            continue
        
        # Check for specific equipment patterns in raw_text
        if 'raw_text' in row and pd.notna(row['raw_text']):
            raw_text = row['raw_text']
            
            # Pattern: "X Brand Model Quantity"
            pattern1 = r'([A-Za-z\s&\-]+)[\s]([A-Za-z0-9\s\-\.]+)[\s]+(\d+)'
            
            # Pattern: "Brand Model X Quantity"
            pattern2 = r'([A-Za-z\s&\-]+)[\s]([A-Za-z0-9\s\-\.]+)[\s]+(\d+)'
            
            # Try to match equipment patterns
            match = re.search(pattern1, raw_text) or re.search(pattern2, raw_text)
            
            if match:
                # Extract information from the match
                if len(match.groups()) >= 3:
                    # Try to determine which part is manufacturer, model, and quantity
                    parts = [p.strip() for p in match.groups()]
                    
                    # Identify numbers which are likely quantities
                    quantity_indices = [i for i, p in enumerate(parts) if p.isdigit()]
                    
                    if quantity_indices:
                        quantity = parts[quantity_indices[0]]
                        # Remove the quantity from parts
                        other_parts = [p for i, p in enumerate(parts) if i not in quantity_indices]
                        
                        # The remaining parts are likely manufacturer and model
                        if len(other_parts) >= 2:
                            manufacturer = other_parts[0]
                            model = ' '.join(other_parts[1:])
                        else:
                            manufacturer = row['manufacturer'] or ''
                            model = other_parts[0]
                        
                        equipment_items.append({
                            'manufacturer': manufacturer,
                            'model': model,
                            'quantity': quantity,
                            'equipment_type': row['equipment_type'],
                            'venue': row['venue']
                        })
                        continue
        
        # If no pattern match, use the row data directly
        item = {
            'manufacturer': row['manufacturer'] if 'manufacturer' in row and pd.notna(row['manufacturer']) else '',
            'model': row['model'],
            'quantity': row['quantity'] if 'quantity' in row and pd.notna(row['quantity']) else '',
            'equipment_type': row['equipment_type'],
            'venue': row['venue']
        }
        equipment_items.append(item)
    
    # Convert to DataFrame
    result_df = pd.DataFrame(equipment_items)
    
    # Clean up the data
    result_df['manufacturer'] = result_df['manufacturer'].str.strip()
    result_df['model'] = result_df['model'].str.strip()
    result_df['quantity'] = result_df['quantity'].str.strip() if result_df['quantity'].dtype == 'object' else result_df['quantity']
    
    # Remove duplicates
    result_df = result_df.drop_duplicates().reset_index(drop=True)
    
    return result_df

def extract_equipment_from_text(raw_text, equipment_type, venue):
    """Extract equipment information from raw text using regex patterns."""
    equipment_items = []
    
    # Define patterns for different equipment formats
    patterns = [
        # Format: "X Brand Model"
        r'(\d+)\s+([A-Za-z\s&\-]+)\s+([A-Za-z0-9\s\-\.]+)',
        
        # Format: "Brand Model X"
        r'([A-Za-z\s&\-]+)\s+([A-Za-z0-9\s\-\.]+)\s+(\d+)',
        
        # Format: "X x Brand Model"
        r'(\d+)\s*[xX]\s*([A-Za-z\s&\-]+)\s+([A-Za-z0-9\s\-\.]+)',
        
        # Format: "Brand Model - X"
        r'([A-Za-z\s&\-]+)\s+([A-Za-z0-9\s\-\.]+)\s*[-–]\s*(\d+)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, raw_text)
        for match in matches:
            # Extract parts
            parts = [p.strip() for p in match.groups()]
            
            # Identify number which is likely quantity
            quantity_indices = [i for i, p in enumerate(parts) if p.isdigit()]
            
            if quantity_indices:
                quantity = parts[quantity_indices[0]]
                # Remove the quantity from parts
                other_parts = [p for i, p in enumerate(parts) if i not in quantity_indices]
                
                # The remaining parts are likely manufacturer and model
                if len(other_parts) >= 2:
                    manufacturer = other_parts[0]
                    model = ' '.join(other_parts[1:])
                else:
                    manufacturer = ''
                    model = other_parts[0]
                
                equipment_items.append({
                    'manufacturer': manufacturer,
                    'model': model,
                    'quantity': quantity,
                    'equipment_type': equipment_type,
                    'venue': venue
                })
    
    return equipment_items

def extract_specific_equipment_types(df):
    """Extract specific types of equipment from the data based on patterns."""
    lighting_patterns = [
        r'Moving Head', r'Fresnel', r'PAR', r'LED', r'Flood', r'Profile', 
        r'Follow Spot', r'Strobe', r'Dimmer', r'Scroller', r'Martin', r'ETC',
        r'Vari-Lite', r'Clay Paky', r'High End', r'Robe', r'Chauvet'
    ]
    
    sound_patterns = [
        r'Speaker', r'Microphone', r'Mic', r'Mixer', r'Console', r'Amplifier', 
        r'Subwoofer', r'Monitor', r'Processor', r'DI Box', r'Shure', r'Sennheiser', 
        r'Yamaha', r'L-Acoustics', r'd&b', r'Meyer', r'DiGiCo', r'Midas'
    ]
    
    video_patterns = [
        r'Projector', r'Screen', r'Display', r'Monitor', r'Camera', r'Switcher', 
        r'Barco', r'Christie', r'Sony', r'Panasonic', r'Extron', r'Kramer', 
        r'Blackmagic'
    ]
    
    # Create pattern matching functions
    def matches_pattern(text, patterns):
        if not text or pd.isna(text):
            return False
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)
    
    # Extract equipment based on patterns
    lighting_equipment = df[
        (df['equipment_type'] == 'lighting') | 
        df['model'].apply(lambda x: matches_pattern(x, lighting_patterns)) |
        df['manufacturer'].apply(lambda x: matches_pattern(x, lighting_patterns))
    ].copy()
    
    sound_equipment = df[
        (df['equipment_type'] == 'sound') | 
        df['model'].apply(lambda x: matches_pattern(x, sound_patterns)) |
        df['manufacturer'].apply(lambda x: matches_pattern(x, sound_patterns))
    ].copy()
    
    video_equipment = df[
        (df['equipment_type'] == 'video') | 
        df['model'].apply(lambda x: matches_pattern(x, video_patterns)) |
        df['manufacturer'].apply(lambda x: matches_pattern(x, video_patterns))
    ].copy()
    
    # Update equipment types
    lighting_equipment['equipment_type'] = 'lighting'
    sound_equipment['equipment_type'] = 'sound'
    video_equipment['equipment_type'] = 'video'
    
    # Combine the results
    combined = pd.concat([lighting_equipment, sound_equipment, video_equipment])
    combined = combined.drop_duplicates().reset_index(drop=True)
    
    return combined

def main():
    """Main function to create final standardized output."""
    # Find standardized data
    standardized_dir = Path(__file__).parent / "output" / "standardized"
    if not standardized_dir.exists():
        print("Standardized data directory not found.")
        return
    
    # Create final output directory
    final_dir = Path(__file__).parent / "output" / "final"
    final_dir.mkdir(exist_ok=True, parents=True)
    
    # Find all standardized files
    all_files = list(standardized_dir.glob("*_standardized.csv"))
    venue_files = list(standardized_dir.glob("*_all_equipment.csv"))
    
    if not all_files:
        print("No standardized data files found.")
        return
    
    print(f"Found {len(all_files)} standardized equipment files.")
    
    # Process each venue's combined data if available
    for venue_file in venue_files:
        venue_name = re.sub(r'_all_equipment\.csv$', '', venue_file.name)
        print(f"\nProcessing venue: {venue_name}")
        
        try:
            # Read the data
            df = pd.read_csv(venue_file)
            
            # Clean the data
            cleaned_df = clean_equipment_data(df)
            
            # Extract specific equipment types
            final_df = extract_specific_equipment_types(cleaned_df)
            
            # Save the final output
            output_file = final_dir / f"{venue_name}_final.csv"
            final_df.to_csv(output_file, index=False)
            print(f"Saved {len(final_df)} equipment items to {output_file}")
            
            # Create separate files for each equipment type
            for eq_type in ['lighting', 'sound', 'video']:
                type_df = final_df[final_df['equipment_type'] == eq_type]
                if not type_df.empty:
                    type_file = final_dir / f"{venue_name}_{eq_type}_final.csv"
                    type_df.to_csv(type_file, index=False)
                    print(f"  - {eq_type.capitalize()}: {len(type_df)} items")
        
        except Exception as e:
            print(f"Error processing {venue_file}: {e}")
    
    # Combine all final data
    final_files = list(final_dir.glob("*_final.csv"))
    if final_files:
        all_data = []
        for file in final_files:
            if not '_lighting_final' in file.name and not '_sound_final' in file.name and not '_video_final' in file.name:
                df = pd.read_csv(file)
                all_data.append(df)
        
        if all_data:
            combined_df = pd.concat(all_data)
            combined_file = final_dir / "all_venues_final.csv"
            combined_df.to_csv(combined_file, index=False)
            print(f"\nSaved {len(combined_df)} total equipment items from all venues to {combined_file}")
    
    print("\nFinal data processing complete!")

if __name__ == "__main__":
    main()