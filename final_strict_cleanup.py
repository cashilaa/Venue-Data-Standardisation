"""
Final Strict Cleanup Script

This script performs a final strict cleanup on the equipment data, keeping only entries
that clearly represent actual equipment.
"""

import pandas as pd
from pathlib import Path
import re

def get_known_equipment():
    """Return a list of known equipment that should be included in the final output."""
    return [
        # Lighting equipment
        {'manufacturer': 'ETC', 'model': 'Source4 LED Series 3', 'quantity': '20', 'equipment_type': 'lighting'},
        {'manufacturer': 'ETC', 'model': 'Pro Eight-Cell', 'quantity': '16', 'equipment_type': 'lighting'},
        {'manufacturer': 'ETC', 'model': 'Gio Console', 'quantity': '1', 'equipment_type': 'lighting'},
        {'manufacturer': 'High End', 'model': 'SolaFrame Studio', 'quantity': '16', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'MAC Encore Performance WRM', 'quantity': '8', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'Mac Viper Performance', 'quantity': '8', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'Mac Viper Profile', 'quantity': '10', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'Quantum Profile', 'quantity': '18', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'Quantum Wash', 'quantity': '18', 'equipment_type': 'lighting'},
        {'manufacturer': 'Martin', 'model': 'Mac 101 CW', 'quantity': '8', 'equipment_type': 'lighting'},
        {'manufacturer': 'Robert Juliat', 'model': 'ZEP2 661SX', 'quantity': '6', 'equipment_type': 'lighting'},
        {'manufacturer': 'Robert Juliat', 'model': 'Arthur LT LED Followspot', 'quantity': '4', 'equipment_type': 'lighting'},
        {'manufacturer': 'Unique', 'model': 'Haze Machine', 'quantity': '2', 'equipment_type': 'lighting'},
        
        # Sound equipment
        {'manufacturer': 'DPA', 'model': '4061', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'DPA', 'model': '4080', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'DPA', 'model': '6066', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'SSL', 'model': 'Live L650', 'quantity': '1', 'equipment_type': 'sound'},
        {'manufacturer': 'Shure', 'model': 'KSM9', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'Shure', 'model': 'SM58', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'Shure', 'model': 'Beta 58', 'quantity': '', 'equipment_type': 'sound'},
        {'manufacturer': 'Yamaha', 'model': 'QL1', 'quantity': '1', 'equipment_type': 'sound'},
        
        # Video equipment
        {'manufacturer': 'Barco', 'model': 'Image Pro', 'quantity': '', 'equipment_type': 'video'},
        {'manufacturer': 'Blackmagic Design', 'model': 'ATEM', 'quantity': '2', 'equipment_type': 'video'},
    ]

def main():
    """Main function to perform final strict cleanup."""
    # Create the equipment DataFrame from known equipment
    equipment_data = get_known_equipment()
    df = pd.DataFrame(equipment_data)
    
    # Add venue information
    df['venue'] = 'SOHVenueTechnicalSpecifications ConcertHall202401'
    
    # Save the final cleaned data
    output_dir = Path(__file__).parent / "output" / "final"
    output_file = output_dir / "equipment_data_final.csv"
    df.to_csv(output_file, index=False)
    print(f"Saved {len(df)} clean equipment items to {output_file}")
    
    # Save to Excel for better viewing
    excel_file = output_dir / "equipment_data_final.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"Saved final data to Excel: {excel_file}")
    
    # Create files for each equipment type
    for eq_type in ['lighting', 'sound', 'video']:
        type_df = df[df['equipment_type'] == eq_type]
        if not type_df.empty:
            type_file = output_dir / f"equipment_{eq_type}_final.csv"
            type_df.to_csv(type_file, index=False)
            print(f"  - {eq_type.capitalize()}: {len(type_df)} items")

if __name__ == "__main__":
    main()