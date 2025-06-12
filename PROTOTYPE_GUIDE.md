# Venue Data Standardisation Prototype Guide

This guide walks you through completing the prototype for standardizing venue technical specifications.

## Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Sample Venues

For this prototype, we recommend using the following venues:

1. **The Music Center at Strathmore**
   - Tech specs: [Strathmore Music Center Production Specifications](https://www.strathmore.org/media/ixspjkbi/strathmore-music-center-production-specifications-01-30-2021.pdf)

2. **Carnegie Hall**
   - Tech specs: [Carnegie Hall Media Kit](https://www.carnegiehall.org/uploadedFiles/Resources_and_Components/PDF/Press/Carnegie_Hall_Media_Kit.pdf)

3. **Hill Auditorium (University of Michigan)**
   - Info: [Hill Auditorium Facilities Page](https://smtd.umich.edu/facilities/hill-auditorium)
   - You may need to search for the technical specifications PDF

## Completing the Prototype

### Step 1: Find Venue Technical Specifications

Run the main script and select option 1:
```
python standardize_venues.py
```

For each venue, search for their technical specifications, focusing on lighting, sound, and video equipment.

### Step 2: Extract Data from PDFs

Once you have downloaded the technical specification PDFs:

1. Run the main script and select option 2
2. Enter the venue name and path to the PDF file
3. The script will extract tables and text from the PDF

### Step 3: Manual Data Review and Cleanup

After extraction, you'll need to:

1. Review the extracted tables in the `data/<venue_name>/` directory
2. Create a cleaned CSV file with proper headers for equipment
3. For each venue, focus on organizing the data into three categories:
   - Lighting equipment
   - Sound equipment
   - Video equipment

### Step 4: Standardize Data

Run the main script and select option 3 to standardize the cleaned data according to our schema.

### Step 5: View Standardized Data

Run the main script and select option 4 to view the standardized venue data.

## Expected Outcome

The prototype should demonstrate:

1. Successful extraction of equipment data from venue technical specifications
2. Standardization of field names across different venues
3. Organized data in a consistent format
4. A workflow that can be expanded to handle more venues

## Limitations and Future Improvements

- The current prototype requires manual review of extracted data
- PDF extraction might not capture all tables correctly
- Future versions could incorporate machine learning for better data extraction
- A web interface could be added for easier data management