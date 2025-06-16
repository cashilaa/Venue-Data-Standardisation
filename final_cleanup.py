"""
Final Cleanup Script

This script performs a final cleanup on the equipment data to remove any remaining
irrelevant or duplicate entries.
"""

import pandas as pd
from pathlib import Path
import re

def is_valid_equipment(row):
    """Check if this row represents valid equipment."""
    # Invalid patterns in manufacturer
    invalid_mfr_patterns = [
        r'^Additional$',
        r'^Technical',
        r'^Audio$',
        r'^Flown$',
        r'^Individual$',
        r'^Fine$',
        r'^Loudspeaker$',
        r'^Console$',
        r'^Both consoles$',
        r'^Video Replay$',
        r'^Mixing Console$',
        r'^Music Stand$',
        r'^Anteroom to Stage$',
        r'^Auditorium Seating$',
        r'^Additional Staging$',
        r'^Stage$',
        r'^B Minimum clearance',
        r'^C Minimum clearance',
        r'^D Anteroom ceiling',
        r'^E Height clearance',
        r'^Plan Dimensions',
        r'^Followspots$',
        r'^Equipment Model',
        r'^Dimmers$',
        r'^Lighting Pods$',
        r'^House Lights$',
        r'^Desk$',
        r'^Acoustic Systems$',
        r'^Acoustic Banners$',
        r'^Base Sound Equipment$',
        r'^Base Lighting Equipment$',
        r'^The table below',
        r'^Smoke and fog machines$',
        r'^Permanent talkback$',
        r'^Projection and Video Monitors$',
        r'^Temporary Show Relay$',
    ]
    
    # Invalid patterns in model
    invalid_model_patterns = [
        r'^Equipment$',
        r'^Dimensions$',
        r'^wing$',
        r'^height$',
        r'^doors$',
        r'^line$',
        r'^extension$',
        r'^front$',
        r'^hire$',
        r'^LT$',
        r'^are$',
        r'^lighting$',
        r'^emulate$',
        r'^additional$',
        r'^control$',
        r'^approximately$',
        r'^Page$',
        r'^and$',
        r'^with$',
        r'^have$',
        r'^is$',
        r'^the$',
        r'^over$',
        r'^sound$',
        r'^Monitors$',
        r'^not$',
        r'^Gio$',
        r'^Hall',
    ]
    
    # Check invalid manufacturer patterns
    for pattern in invalid_mfr_patterns:
        if re.search(pattern, str(row['manufacturer']), re.IGNORECASE):
            return False
    
    # Check invalid model patterns
    for pattern in invalid_model_patterns:
        if re.search(pattern, str(row['model']), re.IGNORECASE):
            return False
    
    # Check for non-equipment rows
    if (str(row['manufacturer']).strip() == 'A maximum rigging load of' and 
        str(row['model']).strip() == '110 tons plus'):
        return False
        
    # Check for model containing newlines
    if '\n' in str(row['model']):
        return False
        
    # Check for quantities that are clearly not quantities
    if str(row['quantity']).isdigit() and int(row['quantity']) > 100:
        return False
        
    return True

def clean_data(df):
    """Perform final cleaning on the data."""
    # Filter out invalid equipment
    df = df[df.apply(is_valid_equipment, axis=1)].reset_index(drop=True)
    
    # Clean up extra text in model
    df['model'] = df['model'].str.replace(r'\n.*', '', regex=True)
    
    # Remove exact duplicates
    df = df.drop_duplicates().reset_index(drop=True)
    
    # Standardize manufacturer names
    manufacturer_mapping = {
        'ETC 1': 'ETC',
        'Blackmagic': 'Blackmagic Design',
        'MAC': 'Martin',
    }
    
    for old, new in manufacturer_mapping.items():
        df.loc[df['manufacturer'] == old, 'manufacturer'] = new
    
    # Sort by venue, equipment_type, manufacturer
    df = df.sort_values(['venue', 'equipment_type', 'manufacturer']).reset_index(drop=True)
    
    return df

def main():
    """Main function to clean up the final data."""
    # Path to the final CSV file
    input_file = Path(__file__).parent / "output" / "final" / "all_venues_final.csv"
    
    if not input_file.exists():
        print(f"Final data file not found: {input_file}")
        return
    
    # Read the data
    df = pd.read_csv(input_file)
    print(f"Read {len(df)} equipment entries from {input_file}")
    
    # Clean the data
    cleaned_df = clean_data(df)
    print(f"Filtered to {len(cleaned_df)} valid equipment entries")
    
    # Save the cleaned data
    output_file = Path(__file__).parent / "output" / "final" / "equipment_data_cleaned.csv"
    cleaned_df.to_csv(output_file, index=False)
    print(f"Saved cleaned data to {output_file}")
    
    # Save to Excel for better viewing
    excel_file = Path(__file__).parent / "output" / "final" / "equipment_data_cleaned.xlsx"
    cleaned_df.to_excel(excel_file, index=False)
    print(f"Saved cleaned data to Excel: {excel_file}")
    
    # Create files for each venue and equipment type
    for venue in cleaned_df['venue'].unique():
        venue_df = cleaned_df[cleaned_df['venue'] == venue]
        venue_file = Path(__file__).parent / "output" / "final" / f"{venue.replace(' ', '_')}_cleaned.csv"
        venue_df.to_csv(venue_file, index=False)
        print(f"Saved {len(venue_df)} items for venue: {venue}")
        
        # Create files for each equipment type within this venue
        for eq_type in ['lighting', 'sound', 'video']:
            type_df = venue_df[venue_df['equipment_type'] == eq_type]
            if not type_df.empty:
                type_file = Path(__file__).parent / "output" / "final" / f"{venue.replace(' ', '_')}_{eq_type}_cleaned.csv"
                type_df.to_csv(type_file, index=False)
                print(f"  - {eq_type.capitalize()}: {len(type_df)} items")

if __name__ == "__main__":
    main()