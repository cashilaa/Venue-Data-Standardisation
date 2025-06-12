# Venue Data Standardisation

A prototype for standardizing technical specifications from various venues.

## Overview

This project aims to standardize technical equipment data from different venues to create a unified database that artists can use when planning performances.

## Project Structure

- `data/`: Contains raw venue technical specifications
- `schema/`: Defines the standardized data schema and field mappings
- `scripts/`: Python scripts for data extraction and standardization
- `output/`: Standardized venue data output

## Quick Start

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the main application:
   ```
   python standardize_venues.py
   ```

3. For a quick demonstration of the standardization process:
   ```
   python scripts/standardize_venue_data.py
   ```
   This will process the example venue data included in the project.

## Process

1. Collect technical specifications from venues (PDFs, websites)
2. Extract relevant equipment information
3. Map different field names to standardized schema
4. Output standardized data for each venue

## Sample Venues

The prototype includes example data for lighting, sound, and video equipment. For a complete guide on how to standardize data from real venues, see the `PROTOTYPE_GUIDE.md` file.