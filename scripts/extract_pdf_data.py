"""
Utility script to extract data from PDF technical specifications.

Note: This script requires PyPDF2 and tabula-py packages:
    pip install PyPDF2 tabula-py pandas
"""

import os
import sys
import re
import pandas as pd
import json
from pathlib import Path
try:
    import PyPDF2
    import tabula
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyPDF2 tabula-py pandas")
    sys.exit(1)

def extract_tables_from_pdf(pdf_path):
    """Extract tables from a PDF file using tabula."""
    try:
        # Try to extract tables
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        return tables
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return []

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

def save_extracted_data(venue_name, tables, text):
    """Save extracted data to files."""
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data" / venue_name
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Save the full text
    text_file = data_dir / "extracted_text.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Save each table as CSV and combined as JSON
    all_tables = []
    for i, table in enumerate(tables):
        if not table.empty:
            # Save as CSV
            csv_file = data_dir / f"table_{i+1}.csv"
            table.to_csv(csv_file, index=False)
            
            # Add to combined tables
            table_dict = table.to_dict('records')
            if table_dict:
                all_tables.append({
                    "table_number": i+1,
                    "data": table_dict
                })
    
    # Save combined tables as JSON
    json_file = data_dir / "extracted_tables.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_tables, f, indent=2)
    
    print(f"Extracted data for {venue_name} saved to {data_dir}")
    print(f"  - Full text: {text_file}")
    print(f"  - Tables: {len(tables)} tables extracted")
    if tables:
        print(f"  - Combined tables: {json_file}")

def process_pdf(venue_name, pdf_path):
    """Process a PDF file and extract its content."""
    print(f"Processing PDF for {venue_name}...")
    
    # Extract tables and text
    tables = extract_tables_from_pdf(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    # Save the extracted data
    save_extracted_data(venue_name, tables, text)
    
    return tables, text

def main():
    """Main function to extract data from PDFs."""
    if len(sys.argv) < 3:
        print("Usage: python extract_pdf_data.py <venue_name> <pdf_path>")
        sys.exit(1)
    
    venue_name = sys.argv[1]
    pdf_path = sys.argv[2]
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    process_pdf(venue_name, pdf_path)

if __name__ == "__main__":
    main()