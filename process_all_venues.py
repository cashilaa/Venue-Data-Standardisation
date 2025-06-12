"""
Process All Venues Script

This script automatically processes all PDF files in the data directory,
extracts technical specifications, and standardizes the data.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
import re
import warnings
import csv

# Attempt to import PDF processing libraries
try:
    import PyPDF2
    import tabula
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyPDF2 tabula-py pandas")
    sys.exit(1)

# Add the schema directory to the path
sys.path.insert(0, str(Path(__file__).parent))
from schema.field_mapping import standardize_field_name, determine_equipment_type, load_schema

def extract_text_from_pdf(pdf_path):
    """Extract full text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        return text
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""

def extract_tables_from_pdf(pdf_path):
    """Extract tables from a PDF file using tabula."""
    try:
        # Try to extract tables
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

def identify_venue_name(pdf_path):
    """Try to identify the venue name from the PDF filename or content."""
    # First, try to extract from filename
    filename = Path(pdf_path).stem
    # Clean up the filename to get a reasonable venue name
    venue_name = filename.replace('_', ' ').replace('-', ' ')
    
    # If the filename is just numbers or too short, try to extract from content
    if venue_name.isdigit() or len(venue_name) < 5:
        # Extract first page text and look for venue name patterns
        try:
            text = extract_text_from_pdf(pdf_path)
            # Look for patterns like "XXX Theatre", "XXX Venue", "XXX Hall", etc.
            venue_patterns = [
                r"([A-Z][a-zA-Z\s]+) (Theatre|Theater|Hall|Venue|Auditorium|Arena|Stadium)",
                r"(Sydney Opera House|Royal Albert Hall|Carnegie Hall|Lincoln Center)",
                r"TECHNICAL SPECIFICATIONS[:\s]+(.*?)[\n\r]",
                r"VENUE[:\s]+(.*?)[\n\r]"
            ]
            
            for pattern in venue_patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    return matches.group(0).strip()
        except:
            pass
    
    return venue_name

def guess_equipment_type(table_df):
    """Guess the equipment type (lighting, sound, video) based on table content."""
    # Convert the entire DataFrame to string for easier pattern matching
    text = table_df.to_string().lower()
    
    # Define pattern dictionaries for each equipment type
    lighting_patterns = ['light', 'lamp', 'dimmer', 'par', 'led', 'fresnel', 'ellipsoidal', 'moving head', 'beam', 'wash', 'spot', 'strobe', 'dmx']
    sound_patterns = ['speaker', 'microphone', 'mic', 'audio', 'mixer', 'console', 'amplifier', 'amp', 'subwoofer', 'monitor', 'eq', 'equalizer', 'processor', 'di box']
    video_patterns = ['projector', 'screen', 'display', 'monitor', 'camera', 'hdmi', 'vga', 'sdi', 'switcher', 'video', 'resolution', 'media server']
    
    # Count matches for each category
    lighting_count = sum(1 for pattern in lighting_patterns if pattern in text)
    sound_count = sum(1 for pattern in sound_patterns if pattern in text)
    video_count = sum(1 for pattern in video_patterns if pattern in text)
    
    # Return the category with the most matches
    counts = {
        "lighting": lighting_count,
        "sound": sound_count,
        "video": video_count
    }
    
    max_count = max(counts.values())
    if max_count == 0:
        return "unknown"
    
    return max(counts, key=counts.get)

def clean_table(df):
    """Clean and normalize a DataFrame extracted from a PDF table."""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Remove unnamed or empty columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Drop completely empty rows and columns
    df = df.dropna(how='all').dropna(axis=1, how='all')
    
    # Replace NaN with empty string
    df = df.fillna('')
    
    # Clean column names: remove newlines, extra spaces, and normalize
    df.columns = [str(col).strip().replace('\n', ' ').replace('\r', '') for col in df.columns]
    df.columns = [re.sub(r'\s+', ' ', col) for col in df.columns]
    
    # Try to ensure we have model and quantity columns
    column_mapping = {}
    for col in df.columns:
        lower_col = col.lower()
        if any(term in lower_col for term in ['model', 'type', 'fixture', 'instrument']):
            column_mapping[col] = 'Model'
        elif any(term in lower_col for term in ['qty', 'quantity', 'count', 'amount', 'no.', '#']):
            column_mapping[col] = 'Quantity'
        elif any(term in lower_col for term in ['brand', 'make', 'manufacturer']):
            column_mapping[col] = 'Manufacturer'
    
    # Apply mapping if we found relevant columns
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    return df

def process_venue_pdf(pdf_path):
    """Process a venue PDF and extract equipment information."""
    venue_name = identify_venue_name(pdf_path)
    print(f"\nProcessing venue: {venue_name}")
    print(f"PDF: {pdf_path}")
    
    # Create directory for this venue
    venue_dir = Path(__file__).parent / "data" / venue_name.replace(" ", "_")
    venue_dir.mkdir(exist_ok=True, parents=True)
    
    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)
    text_file = venue_dir / "extracted_text.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extracted text saved to: {text_file}")
    
    # Extract tables from PDF
    tables = extract_tables_from_pdf(pdf_path)
    print(f"Extracted {len(tables)} tables from PDF")
    
    # Process each table
    equipment_data = {
        "lighting": [],
        "sound": [],
        "video": []
    }
    
    for i, table in enumerate(tables):
        if table.empty:
            continue
        
        # Clean the table
        cleaned_table = clean_table(table)
        
        # Save the cleaned table as CSV
        csv_path = venue_dir / f"table_{i+1}.csv"
        cleaned_table.to_csv(csv_path, index=False)
        
        # Try to determine the equipment type
        equipment_type = guess_equipment_type(cleaned_table)
        
        # Add equipment type to the table data
        table_dict = cleaned_table.to_dict('records')
        for item in table_dict:
            item['equipment_type'] = equipment_type
            # Add the equipment to the appropriate category
            equipment_data[equipment_type].append(item)
    
    # Save the combined equipment data as JSON
    equipment_file = venue_dir / "equipment_data.json"
    with open(equipment_file, 'w', encoding='utf-8') as f:
        json.dump(equipment_data, f, indent=2)
    
    print(f"Extracted equipment data saved to: {equipment_file}")
    return venue_name, equipment_data

def standardize_equipment_data(venue_name, equipment_data):
    """Standardize the equipment data according to our schema."""
    output_dir = Path(__file__).parent / "output" / venue_name.replace(" ", "_")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Get our schema
    schema = load_schema()
    
    # Process each equipment type
    for equipment_type, items in equipment_data.items():
        if not items:
            continue
        
        # Convert to DataFrame
        df = pd.DataFrame(items)
        
        # Standardize column names
        rename_dict = {col: standardize_field_name(col) for col in df.columns}
        df = df.rename(columns=rename_dict)
        
        # Ensure required fields exist
        for eq_schema in schema["equipment_types"]:
            if eq_schema["type"] == equipment_type:
                for field in eq_schema["fields"]:
                    if field["required"] and field["name"] not in df.columns:
                        df[field["name"]] = None
        
        # Save standardized data
        output_csv = output_dir / f"{equipment_type}_equipment.csv"
        df.to_csv(output_csv, index=False)
        
        output_json = output_dir / f"{equipment_type}_equipment.json"
        df.to_json(output_json, orient="records", indent=2)
        
        print(f"Standardized {equipment_type} equipment data saved to:")
        print(f"  - {output_csv}")
        print(f"  - {output_json}")

def main():
    """Main function to process all venue PDFs."""
    # Find all PDFs in the data directory
    data_dir = Path(__file__).parent / "data"
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process.")
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            venue_name, equipment_data = process_venue_pdf(pdf_file)
            standardize_equipment_data(venue_name, equipment_data)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    print("\nAll venues processed successfully!")

if __name__ == "__main__":
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        main()