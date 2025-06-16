"""
Data Standardizer Module

This module handles the standardization of extracted equipment data.
It maps various field names to standardized schema and ensures consistent output formats.
"""

import json
import re
import pandas as pd
from pathlib import Path

class DataStandardizer:
    """Handles data standardization, field mapping, and output formatting."""
    
    def __init__(self):
        """Initialize the data standardizer with field mappings and schema."""
        # Define the standardized equipment schema
        self.equipment_schema = {
            "lighting": {
                "required_fields": ["model", "manufacturer", "quantity"],
                "optional_fields": ["power", "dmx_channels", "beam_angle", "color", "notes"],
                "field_aliases": {
                    "model": ["model", "model_type", "name", "fixture_type", "type", "description"],
                    "manufacturer": ["brand", "make", "manufacturer", "company", "mfg"],
                    "quantity": ["qty", "count", "amount", "units", "quantity", "number"],
                    "power": ["wattage", "power_consumption", "watts", "w", "power"],
                    "dmx_channels": ["channels", "dmx", "channel_count", "ch", "dmx_channels"],
                    "beam_angle": ["angle", "beam", "spread", "beam_angle"],
                    "color": ["color_type", "color_mode", "colors", "colour"],
                    "notes": ["comments", "additional_info", "description", "remarks", "notes"]
                }
            },
            "sound": {
                "required_fields": ["model", "manufacturer", "quantity"],
                "optional_fields": ["power", "frequency_response", "max_spl", "notes"],
                "field_aliases": {
                    "model": ["model", "model_type", "name", "type", "description"],
                    "manufacturer": ["brand", "make", "manufacturer", "company", "mfg"],
                    "quantity": ["qty", "count", "amount", "units", "quantity", "number"],
                    "power": ["wattage", "power_consumption", "watts", "w", "power"],
                    "frequency_response": ["frequency", "response", "freq_range", "frequency_response"],
                    "max_spl": ["spl", "max_volume", "output", "max_spl", "sound_pressure"],
                    "notes": ["comments", "additional_info", "description", "remarks", "notes"]
                }
            },
            "video": {
                "required_fields": ["model", "manufacturer", "quantity"],
                "optional_fields": ["resolution", "input_types", "notes"],
                "field_aliases": {
                    "model": ["model", "model_type", "name", "type", "description"],
                    "manufacturer": ["brand", "make", "manufacturer", "company", "mfg"],
                    "quantity": ["qty", "count", "amount", "units", "quantity", "number"],
                    "resolution": ["res", "display_resolution", "output_resolution", "resolution"],
                    "input_types": ["inputs", "connections", "input_connections", "connectors"],
                    "notes": ["comments", "additional_info", "description", "remarks", "notes"]
                }
            },
            "other": {
                "required_fields": ["model", "quantity"],
                "optional_fields": ["manufacturer", "notes"],
                "field_aliases": {
                    "model": ["model", "model_type", "name", "type", "description"],
                    "manufacturer": ["brand", "make", "manufacturer", "company", "mfg"],
                    "quantity": ["qty", "count", "amount", "units", "quantity", "number"],
                    "notes": ["comments", "additional_info", "description", "remarks", "notes"]
                }
            }
        }
        
        # Build reverse mapping for field standardization
        self.field_mapping = self._build_field_mapping()
    
    def _build_field_mapping(self):
        """Build a comprehensive field mapping dictionary."""
        mapping = {}
        
        for equipment_type, schema in self.equipment_schema.items():
            for standard_field, aliases in schema["field_aliases"].items():
                for alias in aliases:
                    # Normalize the alias (lowercase, replace special chars with underscores)
                    normalized_alias = re.sub(r'[^a-zA-Z0-9]', '_', alias.lower())
                    mapping[normalized_alias] = standard_field
        
        return mapping
    
    def standardize_field_name(self, raw_field_name):
        """Convert a raw field name to its standardized equivalent."""
        if not raw_field_name:
            return raw_field_name
        
        # Normalize the input field name
        normalized_name = re.sub(r'[^a-zA-Z0-9]', '_', raw_field_name.lower())
        
        # Return the standardized field name if found, otherwise return the original
        return self.field_mapping.get(normalized_name, raw_field_name)
    
    def clean_and_validate_data(self, equipment_item, equipment_type):
        """Clean and validate a single equipment item."""
        if not equipment_item:
            return None
        
        schema = self.equipment_schema.get(equipment_type, self.equipment_schema["other"])
        standardized_item = {}
        
        # Process each field in the item
        for field_name, value in equipment_item.items():
            if not value or (isinstance(value, str) and not value.strip()):
                continue
            
            # Standardize the field name
            standard_field = self.standardize_field_name(field_name)
            
            # Clean the value based on field type
            cleaned_value = self._clean_field_value(standard_field, value)
            
            if cleaned_value:
                standardized_item[standard_field] = cleaned_value
        
        # Ensure required fields are present
        if not self._validate_required_fields(standardized_item, schema):
            return None
        
        # Add equipment type
        standardized_item['equipment_type'] = equipment_type
        
        return standardized_item
    
    def _clean_field_value(self, field_name, value):
        """Clean a field value based on its type."""
        if not value:
            return ""
        
        value = str(value).strip()
        
        if field_name == 'model':
            return self._clean_model_name(value)
        elif field_name == 'manufacturer':
            return self._clean_manufacturer_name(value)
        elif field_name == 'quantity':
            return self._clean_quantity(value)
        elif field_name in ['power', 'dmx_channels', 'max_spl']:
            return self._clean_numeric_field(value)
        elif field_name == 'frequency_response':
            return self._clean_frequency_response(value)
        elif field_name == 'resolution':
            return self._clean_resolution(value)
        else:
            # General text cleaning
            return self._clean_text_field(value)
    
    def _clean_model_name(self, value):
        """Clean model name field."""
        if not value:
            return ""
        
        # Remove common prefixes
        value = re.sub(r'^(Type|Model|Name|Description|Item)\s*[:;-]\s*', '', value, flags=re.IGNORECASE)
        
        # Remove quantity indicators
        value = re.sub(r'\d+\s*[x×]\s*', '', value)
        
        # Clean up punctuation and whitespace
        value = value.strip('.,:;-')
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Validate length
        if len(value) < 2 or len(value) > 100:
            return ""
        
        return value
    
    def _clean_manufacturer_name(self, value):
        """Clean manufacturer name field."""
        if not value:
            return ""
        
        # Remove common prefixes
        value = re.sub(r'^(Brand|Make|Manufacturer|Company|Mfg)\s*[:;-]\s*', '', value, flags=re.IGNORECASE)
        
        # Clean up punctuation and whitespace
        value = value.strip('.,:;-')
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Validate length
        if len(value) < 2 or len(value) > 50:
            return ""
        
        return value
    
    def _clean_quantity(self, value):
        """Clean quantity field."""
        if not value:
            return ""
        
        # Extract numeric value
        match = re.search(r'(\d+)', str(value))
        if match:
            return match.group(1)
        
        return ""
    
    def _clean_numeric_field(self, value):
        """Clean numeric fields like power, channels, etc."""
        if not value:
            return ""
        
        # Extract numeric value with optional unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*([A-Za-z]*)', str(value))
        if match:
            number = match.group(1)
            unit = match.group(2)
            return f"{number}{unit}" if unit else number
        
        return ""
    
    def _clean_frequency_response(self, value):
        """Clean frequency response field."""
        if not value:
            return ""
        
        # Look for frequency range patterns
        match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Hz|kHz)?\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:Hz|kHz)?', str(value), re.IGNORECASE)
        if match:
            return f"{match.group(1)}-{match.group(2)} Hz"
        
        return str(value).strip()
    
    def _clean_resolution(self, value):
        """Clean resolution field."""
        if not value:
            return ""
        
        # Look for resolution patterns
        match = re.search(r'(\d+)\s*[x×]\s*(\d+)', str(value))
        if match:
            width, height = int(match.group(1)), int(match.group(2))
            # Validate reasonable resolution values
            if 100 <= width <= 10000 and 100 <= height <= 10000:
                return f"{width}x{height}"
        
        return str(value).strip()
    
    def _clean_text_field(self, value):
        """Clean general text fields."""
        if not value:
            return ""
        
        # Clean up whitespace and punctuation
        value = re.sub(r'\s+', ' ', str(value)).strip()
        value = value.strip('.,:;-')
        
        # Validate length
        if len(value) > 500:  # Truncate very long text
            value = value[:500] + "..."
        
        return value
    
    def _validate_required_fields(self, item, schema):
        """Validate that required fields are present and valid."""
        required_fields = schema.get("required_fields", [])
        
        for field in required_fields:
            if field not in item or not item[field]:
                return False
        
        return True
    
    def standardize_venue_data(self, venue_data):
        """Standardize all equipment data for a single venue."""
        if not venue_data or 'equipment' not in venue_data:
            return None
        
        standardized_equipment = []
        
        for equipment_item in venue_data['equipment']:
            equipment_type = equipment_item.get('equipment_type', 'other')
            
            # Clean and validate the equipment item
            standardized_item = self.clean_and_validate_data(equipment_item, equipment_type)
            
            if standardized_item:
                # Add venue information
                standardized_item['venue_name'] = venue_data['venue_name']
                standardized_item['pdf_source'] = venue_data.get('pdf_source', '')
                
                standardized_equipment.append(standardized_item)
        
        # Remove duplicates
        standardized_equipment = self._remove_duplicates(standardized_equipment)
        
        return {
            'venue_name': venue_data['venue_name'],
            'pdf_source': venue_data.get('pdf_source', ''),
            'equipment': standardized_equipment,
            'total_items': len(standardized_equipment)
        }
    
    def _remove_duplicates(self, equipment_list):
        """Remove duplicate equipment items."""
        unique_items = []
        seen_items = set()
        
        for item in equipment_list:
            # Create a key for deduplication based on model, manufacturer, and quantity
            key = (
                item.get('model', '').lower(),
                item.get('manufacturer', '').lower(),
                item.get('quantity', ''),
                item.get('equipment_type', '')
            )
            
            if key not in seen_items:
                seen_items.add(key)
                unique_items.append(item)
        
        return unique_items
    
    def standardize_all_venues(self, venues_data):
        """Standardize equipment data for all venues."""
        standardized_venues = []
        
        for venue_data in venues_data:
            standardized_venue = self.standardize_venue_data(venue_data)
            if standardized_venue and standardized_venue['equipment']:
                standardized_venues.append(standardized_venue)
        
        return standardized_venues
    
    def export_to_csv(self, standardized_data, output_file):
        """Export standardized data to CSV format."""
        all_equipment = []
        
        # Flatten all equipment from all venues
        for venue in standardized_data:
            all_equipment.extend(venue['equipment'])
        
        if not all_equipment:
            print("No equipment data to export")
            return
        
        # Create DataFrame
        df = pd.DataFrame(all_equipment)
        
        # Ensure consistent column order
        standard_columns = [
            'venue_name', 'equipment_type', 'model', 'manufacturer', 'quantity',
            'power', 'dmx_channels', 'frequency_response', 'max_spl', 'resolution',
            'input_types', 'beam_angle', 'color', 'notes', 'pdf_source'
        ]
        
        # Reorder columns, keeping only those that exist
        existing_columns = [col for col in standard_columns if col in df.columns]
        other_columns = [col for col in df.columns if col not in standard_columns]
        final_columns = existing_columns + other_columns
        
        df = df[final_columns]
        
        # Sort by venue name, then equipment type, then model
        df = df.sort_values(['venue_name', 'equipment_type', 'model'])
        
        # Export to CSV
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"  📊 Exported {len(df)} equipment items to CSV")
    
    def export_to_json(self, standardized_data, output_file):
        """Export standardized data to JSON format."""
        # Create a structured JSON output
        json_data = {
            'metadata': {
                'total_venues': len(standardized_data),
                'total_equipment': sum(len(venue['equipment']) for venue in standardized_data),
                'equipment_types': list(set(
                    item['equipment_type'] 
                    for venue in standardized_data 
                    for item in venue['equipment']
                )),
                'schema_version': '1.0'
            },
            'venues': []
        }
        
        for venue in standardized_data:
            # Group equipment by type for better organization
            equipment_by_type = {}
            for item in venue['equipment']:
                eq_type = item['equipment_type']
                if eq_type not in equipment_by_type:
                    equipment_by_type[eq_type] = []
                equipment_by_type[eq_type].append(item)
            
            venue_data = {
                'venue_name': venue['venue_name'],
                'pdf_source': venue.get('pdf_source', ''),
                'total_equipment': venue['total_items'],
                'equipment_by_type': equipment_by_type,
                'all_equipment': venue['equipment']
            }
            
            json_data['venues'].append(venue_data)
        
        # Export to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"  📄 Exported structured JSON data for {len(standardized_data)} venues")