"""
Extract Venue Information Script

This script extracts technical equipment information from venue PDF files
using text extraction and pattern matching.
"""

import os
import sys
import json
import re
from pathlib import Path
import pandas as pd

# Attempt to import PDF processing libraries
try:
    import PyPDF2
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyPDF2 pandas")
    sys.exit(1)

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
            # Look for patterns like "XXX Theatre", "XXX Hall", etc.
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

def extract_equipment_lists(text):
    """Extract equipment lists from text using pattern matching."""
    equipment_data = {
        "lighting": [],
        "sound": [],
        "video": []
    }
    
    # Look for sections containing equipment information
    sections = {
        "lighting": ["lighting equipment", "lighting inventory", "lighting fixtures", "dimmer", "lantern"],
        "sound": ["sound equipment", "audio equipment", "audio inventory", "sound system", "microphone", "console", "mixing desk"],
        "video": ["video equipment", "projection", "screen", "display", "visual equipment"]
    }
    
    # Find potential equipment lists (numbered or bulleted lists)
    list_patterns = [
        r"(\d+)[\.|\)](.*?)(?=(?:\d+)[\.|\)]|\Z)",  # Numbered lists: 1. Item 1, 2. Item 2
        r"[\•|\-|\*|\–](.*?)(?=[\•|\-|\*|\–]|\Z)",  # Bulleted lists: • Item 1, • Item 2
        r"([A-Za-z\s]+):\s*(\d+)[x|\s]([A-Za-z0-9\s\-\(\)]+)"  # Format: Item name: 10x Description
    ]
    
    # Extract quantities and models using common patterns
    quantity_model_patterns = [
        r"(\d+)\s*[x|×]\s*([A-Za-z0-9\s\-\(\)\'\"\.]+)",  # 10x Item description
        r"([A-Za-z0-9\s\-\(\)\'\"\.]+)\s*:\s*(\d+)",  # Item description: 10
        r"([A-Za-z0-9\s\-\(\)\'\"\.]+)\s*[-|–]\s*(\d+)",  # Item description - 10
    ]
    
    # For each equipment type, look for relevant sections and extract equipment
    for eq_type, keywords in sections.items():
        for keyword in keywords:
            # Find sections containing the keyword
            keyword_pattern = re.compile(r"(?i)(?:^|\n).*?" + keyword + r".*?(?:\n|$)(.*?)(?=(?:^|\n).*?(?:" + "|".join(["lighting", "sound", "audio", "video", "power", "rigging", "staging", "dimensions", "specifications"]) + r").*?(?:\n|$)|\Z)", re.DOTALL)
            
            section_matches = keyword_pattern.findall(text)
            
            for section in section_matches:
                # Try to extract equipment from this section
                for pattern in list_patterns:
                    matches = re.findall(pattern, section, re.MULTILINE)
                    for match in matches:
                        # Normalize the match format
                        if isinstance(match, tuple):
                            if len(match) == 2:  # Simple numbered or bulleted list
                                item = match[1].strip()
                                
                                # Try to extract quantity and model
                                for qm_pattern in quantity_model_patterns:
                                    qm_match = re.search(qm_pattern, item)
                                    if qm_match:
                                        if qm_pattern.startswith(r"(\d+)"):  # Quantity first
                                            quantity = qm_match.group(1)
                                            model = qm_match.group(2).strip()
                                        else:  # Model first
                                            model = qm_match.group(1).strip()
                                            quantity = qm_match.group(2)
                                        
                                        equipment_data[eq_type].append({
                                            "model": model,
                                            "quantity": quantity,
                                            "equipment_type": eq_type,
                                            "raw_text": item
                                        })
                                        break
                                else:
                                    # If no quantity-model pattern matched, just store the raw text
                                    equipment_data[eq_type].append({
                                        "raw_text": item,
                                        "equipment_type": eq_type
                                    })
                            elif len(match) == 3:  # Item: Quantity x Description format
                                model = match[0].strip()
                                quantity = match[1].strip()
                                description = match[2].strip()
                                
                                equipment_data[eq_type].append({
                                    "model": model if model else description,
                                    "quantity": quantity,
                                    "equipment_type": eq_type,
                                    "raw_text": f"{model}: {quantity}x {description}"
                                })
                        else:  # Single string match
                            item = match.strip()
                            
                            # Try to extract quantity and model
                            for qm_pattern in quantity_model_patterns:
                                qm_match = re.search(qm_pattern, item)
                                if qm_match:
                                    if qm_pattern.startswith(r"(\d+)"):  # Quantity first
                                        quantity = qm_match.group(1)
                                        model = qm_match.group(2).strip()
                                    else:  # Model first
                                        model = qm_match.group(1).strip()
                                        quantity = qm_match.group(2)
                                    
                                    equipment_data[eq_type].append({
                                        "model": model,
                                        "quantity": quantity,
                                        "equipment_type": eq_type,
                                        "raw_text": item
                                    })
                                    break
                            else:
                                # If no quantity-model pattern matched, just store the raw text
                                equipment_data[eq_type].append({
                                    "raw_text": item,
                                    "equipment_type": eq_type
                                })
    
    # Try to find tables in the text
    table_patterns = [
        # Common table formats with 2-4 columns
        r"([A-Za-z0-9\s\-\(\)\'\"\.]+)\s+(\d+)\s+([A-Za-z0-9\s\-\(\)\'\"\.]+)",  # Model, Quantity, Description
        r"(\d+)\s+([A-Za-z0-9\s\-\(\)\'\"\.]+)\s+([A-Za-z0-9\s\-\(\)\'\"\.]+)",  # Quantity, Model, Description
    ]
    
    for pattern in table_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        for match in matches:
            if len(match) >= 3:
                # Try to determine what each column represents
                if match[0].isdigit():  # First column is likely quantity
                    quantity = match[0]
                    model = match[1]
                    description = match[2] if len(match) > 2 else ""
                elif match[1].isdigit():  # Second column is likely quantity
                    model = match[0]
                    quantity = match[1]
                    description = match[2] if len(match) > 2 else ""
                else:
                    continue  # Skip if we can't identify quantity
                
                # Try to determine equipment type
                eq_type = "unknown"
                if any(keyword in model.lower() or keyword in description.lower() 
                       for keyword in ["light", "dimmer", "par", "fresnel", "profile", "flood"]):
                    eq_type = "lighting"
                elif any(keyword in model.lower() or keyword in description.lower() 
                         for keyword in ["speaker", "mic", "audio", "sound", "console"]):
                    eq_type = "sound"
                elif any(keyword in model.lower() or keyword in description.lower() 
                         for keyword in ["projector", "screen", "video", "display"]):
                    eq_type = "video"
                
                if eq_type != "unknown":
                    equipment_data[eq_type].append({
                        "model": model,
                        "quantity": quantity,
                        "description": description,
                        "equipment_type": eq_type,
                        "raw_text": f"{model} {quantity} {description}"
                    })
    
    return equipment_data

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
    
    # Extract equipment information from text
    equipment_data = extract_equipment_lists(text)
    
    # Save the equipment data as JSON
    equipment_file = venue_dir / "equipment_data.json"
    with open(equipment_file, 'w', encoding='utf-8') as f:
        json.dump(equipment_data, f, indent=2)
    
    print(f"Extracted equipment data saved to: {equipment_file}")
    
    # Save each equipment type as CSV
    for eq_type, items in equipment_data.items():
        if items:
            df = pd.DataFrame(items)
            csv_file = venue_dir / f"{eq_type}_equipment.csv"
            df.to_csv(csv_file, index=False)
            print(f"Saved {len(items)} {eq_type} equipment items to: {csv_file}")
    
    return venue_name, equipment_data

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
            
            # Print summary
            total_items = sum(len(items) for items in equipment_data.values())
            print(f"\nSummary for {venue_name}:")
            print(f"  Total equipment items extracted: {total_items}")
            for eq_type, items in equipment_data.items():
                print(f"  {eq_type.capitalize()} equipment: {len(items)} items")
            
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
    
    print("\nAll venues processed successfully!")

if __name__ == "__main__":
    main()