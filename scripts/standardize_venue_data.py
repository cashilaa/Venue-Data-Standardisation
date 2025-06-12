"""
Script to standardize venue technical specification data.

This script processes raw venue data and standardizes it according to our schema.
"""

import json
import os
import csv
import sys
from pathlib import Path
import pandas as pd

# Add the parent directory to the path so we can import our schema module
parent_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, parent_dir)
try:
    from schema.field_mapping import standardize_field_name, determine_equipment_type, load_schema
except ModuleNotFoundError:
    # Fallback for direct imports
    sys.path.append(os.path.join(parent_dir, "schema"))
    import field_mapping
    standardize_field_name = field_mapping.standardize_field_name
    determine_equipment_type = field_mapping.determine_equipment_type
    load_schema = field_mapping.load_schema

def load_csv_data(file_path):
    """Load data from a CSV file."""
    return pd.read_csv(file_path)

def load_json_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def standardize_dataframe(df):
    """Standardize a DataFrame according to our schema."""
    # Create a copy to avoid modifying the original
    std_df = df.copy()
    
    # Check for and handle duplicate columns
    if len(std_df.columns) != len(set(std_df.columns)):
        # Get columns with duplicates
        duplicate_cols = std_df.columns[std_df.columns.duplicated()].tolist()
        for col in duplicate_cols:
            # Rename duplicate columns with suffixes
            count = 0
            for i, column in enumerate(std_df.columns):
                if column == col:
                    if count > 0:  # Not the first occurrence
                        new_name = f"{col}_{count}"
                        std_df = std_df.rename(columns={col: new_name})
                    count += 1
    
    # Standardize column names
    rename_dict = {col: standardize_field_name(col) for col in std_df.columns}
    std_df = std_df.rename(columns=rename_dict)
    
    # Try to determine the equipment type
    equipment_type = determine_equipment_type(std_df.columns)
    
    # Add equipment_type column if it doesn't exist
    if 'equipment_type' not in std_df.columns:
        std_df['equipment_type'] = equipment_type
    
    # Ensure required fields exist (add empty columns if needed)
    schema = load_schema()
    for eq_type in schema["equipment_types"]:
        if eq_type["type"] == equipment_type:
            for field in eq_type["fields"]:
                if field["required"] and field["name"] not in std_df.columns:
                    std_df[field["name"]] = None
    
    return std_df

def process_venue_data(venue_name, data_file):
    """Process data for a specific venue and standardize it."""
    file_path = Path(data_file)
    
    # Load data based on file extension
    if file_path.suffix.lower() == '.csv':
        df = load_csv_data(file_path)
    elif file_path.suffix.lower() == '.json':
        data = load_json_data(file_path)
        df = pd.DataFrame(data)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Standardize the data
    std_df = standardize_dataframe(df)
    
    # Create output directory if it doesn't exist
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Save the standardized data
    output_file = output_dir / f"{venue_name}_standardized.csv"
    std_df.to_csv(output_file, index=False)
    
    # Also save as JSON for easy programmatic access
    output_json = output_dir / f"{venue_name}_standardized.json"
    std_df.to_json(output_json, orient="records", indent=2)
    
    print(f"Standardized data for {venue_name} saved to:")
    print(f"  - {output_file}")
    print(f"  - {output_json}")

def main():
    """Main function to process venue data."""
    # Check for command line arguments
    if len(sys.argv) > 2:
        venue_name = sys.argv[1]
        data_file = sys.argv[2]
        try:
            print(f"Processing {venue_name}...")
            process_venue_data(venue_name, data_file)
        except Exception as e:
            print(f"Error processing {venue_name}: {e}")
        return
    
    # Example venue data for demonstration
    venues = [
        ("Example Venue - Lighting", str(Path(__file__).parent.parent / "data" / "example_venue_lighting.csv")),
        ("Example Venue - Sound", str(Path(__file__).parent.parent / "data" / "example_venue_sound.csv")),
        ("Example Venue - Video", str(Path(__file__).parent.parent / "data" / "example_venue_video_fixed.csv")),
    ]
    
    if not venues:
        print("No venues configured. Please add venue data files.")
        return
    
    for venue_name, data_file in venues:
        try:
            print(f"Processing {venue_name}...")
            process_venue_data(venue_name, data_file)
        except Exception as e:
            print(f"Error processing {venue_name}: {e}")

if __name__ == "__main__":
    main()