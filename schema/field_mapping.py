"""
Field mapping utilities for standardizing venue data.
This module provides functions to map various field names to our standardized schema.
"""

import json
import os
import re
from pathlib import Path

# Load the schema
def load_schema():
    """Load the equipment schema from the JSON file."""
    schema_path = Path(__file__).parent / "equipment_schema.json"
    with open(schema_path, 'r') as f:
        return json.load(f)

# Build a mapping of all possible field names to their standardized names
def build_field_mapping():
    """Build a dictionary mapping all possible field names to their standardized names."""
    schema = load_schema()
    mapping = {}
    
    for equipment_type in schema["equipment_types"]:
        for field in equipment_type["fields"]:
            for alias in field["aliases"]:
                # Create a normalized version of the alias (lowercase, spaces to underscores)
                normalized_alias = re.sub(r'[^a-zA-Z0-9]', '_', alias.lower())
                # Map this normalized alias to the standardized field name
                mapping[normalized_alias] = field["name"]
                
    return mapping

# Function to standardize a field name based on our mapping
def standardize_field_name(raw_field_name):
    """Convert a raw field name to its standardized equivalent."""
    field_mapping = build_field_mapping()
    # Normalize the input field name
    normalized_name = re.sub(r'[^a-zA-Z0-9]', '_', raw_field_name.lower())
    
    # Return the standardized field name if found, otherwise return the original
    return field_mapping.get(normalized_name, raw_field_name)

# Get the equipment type from a field set
def determine_equipment_type(fields):
    """Try to determine the equipment type based on the fields present."""
    schema = load_schema()
    
    # Count matching fields for each equipment type
    type_scores = {}
    for equipment_type in schema["equipment_types"]:
        type_name = equipment_type["type"]
        type_scores[type_name] = 0
        
        for field in equipment_type["fields"]:
            if field["name"] in fields:
                type_scores[type_name] += 1
                
    # Return the equipment type with the highest score
    if type_scores:
        return max(type_scores.items(), key=lambda x: x[1])[0]
    return "unknown"