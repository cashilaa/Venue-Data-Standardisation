"""
Venue Data Standardization - Main Runner

This is the main script that orchestrates the entire venue data processing pipeline:
1. Extracts equipment data from venue PDF technical specifications
2. Standardizes the data using field mapping and schema validation
3. Outputs clean, standardized data ready for database import

Usage: python main.py
"""

import os
import sys
from pathlib import Path
import json

# Import our custom modules
from pdf_processor import PDFProcessor
from data_standardizer import DataStandardizer

def main():
    """Main function that runs the complete venue data processing pipeline."""
    print("=" * 60)
    print("VENUE DATA STANDARDIZATION PIPELINE")
    print("=" * 60)
    
    # Initialize processors
    pdf_processor = PDFProcessor()
    data_standardizer = DataStandardizer()
    
    # Define directories
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Step 1: Find and process all PDF files
    print("\n📄 STEP 1: Processing PDF files...")
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in the data directory.")
        print(f"   Please add venue PDF files to: {data_dir}")
        return
    
    print(f"✅ Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF and extract equipment data
    all_venues_data = []
    
    for pdf_file in pdf_files:
        print(f"\n🔄 Processing: {pdf_file.name}")
        try:
            venue_data = pdf_processor.process_venue_pdf(pdf_file)
            if venue_data:
                all_venues_data.append(venue_data)
                print(f"✅ Successfully processed {venue_data['venue_name']}")
            else:
                print(f"⚠️  No equipment data extracted from {pdf_file.name}")
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
    
    if not all_venues_data:
        print("❌ No venue data was successfully extracted. Please check your PDF files.")
        return
    
    # Step 2: Standardize all extracted data
    print(f"\n🔧 STEP 2: Standardizing data from {len(all_venues_data)} venues...")
    
    try:
        standardized_data = data_standardizer.standardize_all_venues(all_venues_data)
        print(f"✅ Successfully standardized data for {len(standardized_data)} venues")
    except Exception as e:
        print(f"❌ Error during standardization: {e}")
        return
    
    # Step 3: Generate final outputs
    print("\n📊 STEP 3: Generating final outputs...")
    
    try:
        # Generate database-ready CSV
        final_csv = output_dir / "venues_equipment_database.csv"
        data_standardizer.export_to_csv(standardized_data, final_csv)
        print(f"✅ Database-ready CSV saved to: {final_csv}")
        
        # Generate JSON for API/web use
        final_json = output_dir / "venues_equipment_database.json"
        data_standardizer.export_to_json(standardized_data, final_json)
        print(f"✅ JSON data saved to: {final_json}")
        
        # Generate summary report
        summary_file = output_dir / "processing_summary.txt"
        generate_summary_report(standardized_data, summary_file)
        print(f"✅ Summary report saved to: {summary_file}")
        
    except Exception as e:
        print(f"❌ Error generating outputs: {e}")
        return
    
    # Final success message
    print("\n" + "=" * 60)
    print("🎉 PROCESSING COMPLETE!")
    print("=" * 60)
    print(f"📁 All outputs saved to: {output_dir}")
    print("\nYour venue equipment data is now ready for database import!")
    print("Artists can now easily browse available equipment at each venue.")

def generate_summary_report(standardized_data, output_file):
    """Generate a human-readable summary report."""
    total_venues = len(standardized_data)
    total_equipment = sum(len(venue['equipment']) for venue in standardized_data)
    
    # Count equipment by type
    equipment_counts = {'lighting': 0, 'sound': 0, 'video': 0, 'other': 0}
    
    for venue in standardized_data:
        for equipment in venue['equipment']:
            eq_type = equipment.get('equipment_type', 'other')
            equipment_counts[eq_type] = equipment_counts.get(eq_type, 0) + 1
    
    # Generate report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("VENUE DATA STANDARDIZATION SUMMARY REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total Venues Processed: {total_venues}\n")
        f.write(f"Total Equipment Items: {total_equipment}\n\n")
        
        f.write("Equipment Breakdown:\n")
        f.write("-" * 20 + "\n")
        for eq_type, count in equipment_counts.items():
            f.write(f"{eq_type.capitalize()}: {count} items\n")
        
        f.write("\nVenue Details:\n")
        f.write("-" * 15 + "\n")
        
        for venue in standardized_data:
            f.write(f"\n{venue['venue_name']}:\n")
            f.write(f"  Total Equipment: {len(venue['equipment'])} items\n")
            
            # Count by type for this venue
            venue_counts = {'lighting': 0, 'sound': 0, 'video': 0, 'other': 0}
            for equipment in venue['equipment']:
                eq_type = equipment.get('equipment_type', 'other')
                venue_counts[eq_type] = venue_counts.get(eq_type, 0) + 1
            
            for eq_type, count in venue_counts.items():
                if count > 0:
                    f.write(f"    {eq_type.capitalize()}: {count} items\n")

if __name__ == "__main__":
    main()