# Venue Data Standardisation

A project for standardizing technical specifications from various venues.

## Overview

This project extracts, processes, and standardizes technical equipment data from venue PDF files to create a unified database that artists can use when planning performances.

## Project Structure

- `data/`: Contains raw venue technical specifications (PDFs)
- `schema/`: Defines the standardized data schema and field mappings
- `/`: Python scripts for data extraction and standardization
- `output/`: Standardized venue data output
  - `standardized/`: Initial standardized data extracted from PDFs
  - `final/`: Final cleaned and standardized equipment data

## Scripts

1. `extract_venue_info.py` - Extracts text and equipment information from venue PDFs
2. `standardize_extracted_data.py` - Initial standardization of extracted data
3. `create_final_output.py` - Creates a structured output of equipment data
4. `improved_final_output.py` - Improved version with better data cleaning
5. `fixed_final_output.py` - Fixed version with enhanced error handling
6. `final_cleanup.py` - Final cleanup to remove irrelevant items
7. `final_strict_cleanup.py` - Final strict cleanup to ensure only valid equipment items remain

## Quick Start

1. Install required dependencies:
   ```
   pip install PyPDF2 pandas
   ```

2. Run the extraction script:
   ```
   python extract_venue_info.py
   ```

3. Run the standardization script:
   ```
   python final_strict_cleanup.py
   ```

## Process

1. **Extract Text from PDFs**: Using PyPDF2 to extract raw text from venue PDF files
2. **Identify Equipment**: Pattern matching and text analysis to identify equipment mentions
3. **Standardize Data**: Clean and standardize equipment data with consistent formatting
4. **Categorize Equipment**: Categorize into lighting, sound, and video equipment
5. **Final Cleanup**: Remove irrelevant entries and duplicates

## Final Output Files

- `equipment_data_final.csv` - Complete list of all venue equipment
- `equipment_lighting_final.csv` - Lighting equipment only
- `equipment_sound_final.csv` - Sound equipment only
- `equipment_video_final.csv` - Video equipment only

## Results

Successfully extracted and standardized equipment data from venue PDFs, creating a structured and clean dataset suitable for venue management and analysis. The final data includes:

- Manufacturer
- Model
- Quantity
- Equipment Type (lighting, sound, video)
- Venue