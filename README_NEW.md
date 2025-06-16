# Venue Data Standardization System

A streamlined 3-file system for extracting and standardizing technical equipment data from venue PDF specifications.

## 🎯 Purpose

This system helps venue management companies populate their databases with standardized equipment information from venue technical specification PDFs. Artists can then easily browse available equipment at each venue when planning their performances.

## 📁 System Architecture

The system consists of just **3 main files**:

1. **`main.py`** - Main runner that orchestrates the entire process
2. **`pdf_processor.py`** - Handles PDF text extraction and equipment parsing
3. **`data_standardizer.py`** - Handles field mapping, standardization, and output formatting

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Your Venue PDFs
Place all venue technical specification PDF files in the `data/` folder.

### 3. Run the System
```bash
python main.py
```

That's it! The system will:
- Extract equipment data from all PDFs
- Standardize field names and formats
- Generate database-ready outputs

## 📊 Output Files

The system generates three main outputs in the `output/` folder:

1. **`venues_equipment_database.csv`** - Database-ready CSV with all equipment
2. **`venues_equipment_database.json`** - Structured JSON for APIs/web applications
3. **`processing_summary.txt`** - Human-readable summary report

## 🔧 Standardized Equipment Schema

The system standardizes equipment into these categories:

### Lighting Equipment
- **Required**: model, manufacturer, quantity
- **Optional**: power, dmx_channels, beam_angle, color, notes

### Sound Equipment
- **Required**: model, manufacturer, quantity
- **Optional**: power, frequency_response, max_spl, notes

### Video Equipment
- **Required**: model, manufacturer, quantity
- **Optional**: resolution, input_types, notes

## 🗺️ Field Mapping

The system automatically maps various field names to standardized ones:

| Raw Field Names | Standardized Field |
|----------------|-------------------|
| "model", "model_type", "name", "fixture_type" | `model` |
| "brand", "make", "manufacturer", "company" | `manufacturer` |
| "qty", "count", "amount", "units" | `quantity` |
| "wattage", "power_consumption", "watts" | `power` |
| "channels", "dmx", "channel_count" | `dmx_channels` |

## 📈 Database Integration

The CSV output is designed for direct database import with these columns:

- `venue_name` - Name of the venue
- `equipment_type` - Category (lighting/sound/video/other)
- `model` - Equipment model name
- `manufacturer` - Equipment manufacturer
- `quantity` - Number of units available
- `power` - Power requirements (if applicable)
- `dmx_channels` - DMX channels (for lighting)
- `frequency_response` - Frequency range (for sound)
- `resolution` - Display resolution (for video)
- `notes` - Additional information
- `pdf_source` - Source PDF file path

## 🎨 For Artists

Once the data is in your database, artists can:
- Search equipment by venue
- Filter by equipment type
- Check availability and specifications
- Plan their technical requirements in advance

## 🔍 Troubleshooting

### No Equipment Found
- Check that PDFs contain readable text (not just images)
- Ensure PDFs have equipment lists or technical specifications
- Try PDFs with clearer formatting

### Poor Data Quality
- The system works best with structured PDFs
- Manual review of outputs is recommended
- Consider preprocessing PDFs for better text extraction

## 📝 Customization

To modify the standardization schema:
1. Edit the `equipment_schema` in `data_standardizer.py`
2. Add new field mappings as needed
3. Adjust cleaning functions for specific requirements

## 🤝 Support

For issues or improvements, check the processing summary report for details on what was extracted from each venue.