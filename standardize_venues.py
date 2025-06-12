"""
Main script for the Venue Data Standardisation project.

This script guides users through the process of standardizing venue technical specifications.
"""

import os
import sys
import subprocess
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the project header."""
    clear_screen()
    print("=" * 80)
    print("VENUE DATA STANDARDISATION".center(80))
    print("=" * 80)
    print()

def print_menu():
    """Print the main menu."""
    print("MAIN MENU")
    print("1. Find venue technical specifications")
    print("2. Extract data from PDF")
    print("3. Standardize venue data")
    print("4. View standardized venue data")
    print("5. Exit")
    print()
    
def find_venue_specs():
    """Run the find_venue_specs.py script."""
    print_header()
    print("FIND VENUE TECHNICAL SPECIFICATIONS")
    print("-----------------------------------")
    
    venue_name = input("Enter venue name: ")
    script_path = Path(__file__).parent / "scripts" / "find_venue_specs.py"
    
    subprocess.run([sys.executable, str(script_path), venue_name])
    
    input("\nPress Enter to return to main menu...")

def extract_pdf_data():
    """Run the extract_pdf_data.py script."""
    print_header()
    print("EXTRACT DATA FROM PDF")
    print("--------------------")
    
    venue_name = input("Enter venue name: ")
    pdf_path = input("Enter path to PDF file: ")
    
    script_path = Path(__file__).parent / "scripts" / "extract_pdf_data.py"
    
    subprocess.run([sys.executable, str(script_path), venue_name, pdf_path])
    
    input("\nPress Enter to return to main menu...")

def standardize_data():
    """Run the standardize_venue_data.py script."""
    print_header()
    print("STANDARDIZE VENUE DATA")
    print("---------------------")
    
    # Get list of venues with extracted data
    data_dir = Path(__file__).parent / "data"
    venues = [d for d in data_dir.iterdir() if d.is_dir()]
    
    if not venues:
        print("No venue data found. Please extract data from PDFs first.")
        input("\nPress Enter to return to main menu...")
        return
    
    print("Available venues:")
    for i, venue in enumerate(venues, 1):
        print(f"{i}. {venue.name}")
    
    try:
        choice = int(input("\nSelect venue (number): "))
        if 1 <= choice <= len(venues):
            venue = venues[choice-1]
            
            # Find extracted tables
            tables_file = venue / "extracted_tables.json"
            if not tables_file.exists():
                print(f"No extracted tables found for {venue.name}.")
                input("\nPress Enter to return to main menu...")
                return
            
            script_path = Path(__file__).parent / "scripts" / "standardize_venue_data.py"
            subprocess.run([sys.executable, str(script_path), venue.name, str(tables_file)])
            
            input("\nPress Enter to return to main menu...")
        else:
            print("Invalid choice.")
            input("\nPress Enter to return to main menu...")
    except ValueError:
        print("Invalid input.")
        input("\nPress Enter to return to main menu...")

def view_standardized_data():
    """View standardized venue data."""
    print_header()
    print("VIEW STANDARDIZED VENUE DATA")
    print("--------------------------")
    
    # Get list of standardized venue data files
    output_dir = Path(__file__).parent / "output"
    if not output_dir.exists():
        print("No standardized data found.")
        input("\nPress Enter to return to main menu...")
        return
    
    data_files = list(output_dir.glob("*_standardized.csv"))
    
    if not data_files:
        print("No standardized data found.")
        input("\nPress Enter to return to main menu...")
        return
    
    print("Available standardized data:")
    for i, file in enumerate(data_files, 1):
        venue_name = file.stem.replace("_standardized", "")
        print(f"{i}. {venue_name}")
    
    try:
        choice = int(input("\nSelect data to view (number): "))
        if 1 <= choice <= len(data_files):
            file = data_files[choice-1]
            
            # On Windows, open the file with the default application
            if os.name == 'nt':
                os.startfile(file)
            # On Mac/Linux, use the 'open' command
            else:
                subprocess.run(['open', file])
            
            input("\nPress Enter to return to main menu...")
        else:
            print("Invalid choice.")
            input("\nPress Enter to return to main menu...")
    except ValueError:
        print("Invalid input.")
        input("\nPress Enter to return to main menu...")

def main():
    """Main function to run the venue data standardisation process."""
    while True:
        print_header()
        print_menu()
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            find_venue_specs()
        elif choice == '2':
            extract_pdf_data()
        elif choice == '3':
            standardize_data()
        elif choice == '4':
            view_standardized_data()
        elif choice == '5':
            print("Exiting. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()