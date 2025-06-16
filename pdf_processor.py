"""
PDF Processor Module

This module handles the extraction of equipment information from venue PDF files.
It uses text extraction and pattern matching to identify and parse technical equipment data.
"""

import re
import json
from pathlib import Path

# Attempt to import PDF processing libraries
try:
    import PyPDF2
except ImportError:
    print("Required packages not installed. Please run:")
    print("pip install PyPDF2 pandas")
    exit(1)

class PDFProcessor:
    """Handles PDF text extraction and equipment data parsing."""
    
    def __init__(self):
        """Initialize the PDF processor with equipment patterns and keywords."""
        # Equipment type keywords for classification
        self.equipment_keywords = {
            "lighting": [
                "lighting", "light", "fixture", "dimmer", "lantern", "par", "fresnel", 
                "profile", "flood", "led", "moving", "wash", "spot", "beam", "strobe",
                "haze", "fog", "dmx", "channel", "circuit", "luminaire"
            ],
            "sound": [
                "sound", "audio", "speaker", "microphone", "mic", "console", "mixer",
                "amplifier", "amp", "monitor", "pa", "system", "wireless", "radio",
                "headset", "earpiece", "di", "direct", "box", "compressor", "eq"
            ],
            "video": [
                "video", "projection", "projector", "screen", "display", "monitor",
                "camera", "led", "wall", "panel", "visual", "hdmi", "sdi", "dvi",
                "switcher", "scaler", "converter", "plasma", "lcd", "oled"
            ]
        }
        
        # Common patterns for extracting equipment information
        self.quantity_patterns = [
            r"(\d+)\s*[x×]\s*([A-Za-z0-9\s\-\(\)\'\"\.]+)",  # 10x Item description
            r"([A-Za-z0-9\s\-\(\)\'\"\.]+)\s*[:\-]\s*(\d+)",  # Item description: 10
            r"(\d+)\s+([A-Za-z0-9\s\-\(\)\'\"\.]+)",  # 10 Item description
        ]
        
        # List patterns for structured data
        self.list_patterns = [
            r"(\d+)[\.|\)](.*?)(?=(?:\d+)[\.|\)]|\Z)",  # Numbered lists: 1. Item 1, 2. Item 2
            r"[\•|\-|\*|\–](.*?)(?=[\•|\-|\*|\–]|\Z)",  # Bulleted lists: • Item 1, • Item 2
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract full text from a PDF file using PyPDF2."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def identify_venue_name(self, pdf_path, text=""):
        """Try to identify the venue name from the PDF filename or content."""
        # First, try to extract from filename
        filename = Path(pdf_path).stem
        venue_name = filename.replace('_', ' ').replace('-', ' ')
        
        # If the filename is just numbers or too short, try to extract from content
        if venue_name.isdigit() or len(venue_name) < 5:
            if not text:
                text = self.extract_text_from_pdf(pdf_path)
            
            # Look for venue name patterns in the text
            venue_patterns = [
                r"([A-Z][a-zA-Z\s]+)\s+(Theatre|Theater|Hall|Venue|Auditorium|Arena|Stadium|Opera House)",
                r"(Sydney Opera House|Royal Albert Hall|Carnegie Hall|Lincoln Center|Barbican)",
                r"VENUE[:\s]+(.*?)[\n\r]",
                r"TECHNICAL SPECIFICATIONS[:\s]+(.*?)[\n\r]",
                r"^([A-Z][A-Za-z\s]{10,50})\s*$"  # Standalone venue names
            ]
            
            for pattern in venue_patterns:
                matches = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if matches:
                    potential_name = matches.group(1).strip() if len(matches.groups()) > 1 else matches.group(0).strip()
                    if len(potential_name) > 5 and len(potential_name) < 100:
                        return potential_name
        
        return venue_name
    
    def classify_equipment_type(self, text):
        """Determine the equipment type based on keywords in the text."""
        text_lower = text.lower()
        scores = {eq_type: 0 for eq_type in self.equipment_keywords}
        
        for eq_type, keywords in self.equipment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[eq_type] += 1
        
        # Return the type with the highest score, or 'other' if no clear match
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'other'
    
    def extract_equipment_from_text(self, text):
        """Extract equipment information from text using pattern matching."""
        equipment_items = []
        
        # Split text into sections for better processing
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            # Skip very short sections
            if len(section.strip()) < 10:
                continue
            
            # Try numbered and bulleted lists first
            for pattern in self.list_patterns:
                matches = re.findall(pattern, section, re.MULTILINE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple):
                        item_text = match[1].strip() if len(match) > 1 else match[0].strip()
                    else:
                        item_text = match.strip()
                    
                    if len(item_text) > 5 and len(item_text) < 200:
                        equipment_items.append(self.parse_equipment_item(item_text))
            
            # Try quantity patterns
            for pattern in self.quantity_patterns:
                matches = re.findall(pattern, section)
                for match in matches:
                    if len(match) == 2:
                        # Determine which part is quantity and which is description
                        if match[0].isdigit():
                            quantity, description = match[0], match[1].strip()
                        elif match[1].isdigit():
                            description, quantity = match[0].strip(), match[1]
                        else:
                            continue
                        
                        if len(description) > 3:
                            equipment_items.append(self.parse_equipment_item(description, quantity))
            
            # Look for table-like structures
            lines = section.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 10 and len(line) < 200:
                    # Check if line looks like equipment (contains alphanumeric and some numbers)
                    if re.search(r'[A-Za-z]', line) and re.search(r'\d', line):
                        # Skip lines that are clearly headers or page numbers
                        if not re.match(r'^\s*(page|section|chapter|\d+)\s*$', line, re.IGNORECASE):
                            equipment_items.append(self.parse_equipment_item(line))
        
        # Remove duplicates and filter out invalid items
        unique_items = []
        seen_items = set()
        
        for item in equipment_items:
            if item and item.get('model'):
                # Create a key for deduplication
                key = (item['model'].lower(), item.get('quantity', ''))
                if key not in seen_items:
                    seen_items.add(key)
                    unique_items.append(item)
        
        return unique_items
    
    def parse_equipment_item(self, text, quantity=None):
        """Parse a single equipment item from text."""
        if not text or len(text.strip()) < 3:
            return None
        
        text = text.strip()
        
        # Extract quantity if not provided
        if not quantity:
            quantity_match = re.search(r'(\d+)\s*[x×]', text)
            if quantity_match:
                quantity = quantity_match.group(1)
                # Remove the quantity part from the text
                text = re.sub(r'\d+\s*[x×]\s*', '', text, count=1).strip()
        
        # Clean up the model name
        model = self.clean_model_name(text)
        if not model:
            return None
        
        # Extract manufacturer if possible
        manufacturer = self.extract_manufacturer(model)
        
        # Determine equipment type
        equipment_type = self.classify_equipment_type(text)
        
        # Extract additional technical specifications
        specs = self.extract_technical_specs(text)
        
        item = {
            'model': model,
            'manufacturer': manufacturer,
            'quantity': quantity or '',
            'equipment_type': equipment_type,
            'raw_text': text,
            **specs  # Add any extracted technical specifications
        }
        
        return item
    
    def clean_model_name(self, text):
        """Clean and standardize model names."""
        if not text:
            return ""
        
        # Remove common prefixes
        text = re.sub(r'^(Type|Model|Name|Description|Item)\s*[:;-]\s*', '', text, flags=re.IGNORECASE)
        
        # Remove quantity indicators
        text = re.sub(r'\d+\s*[x×]\s*', '', text)
        
        # Remove trailing punctuation and whitespace
        text = text.strip('.,:;-')
        
        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove very short or very long strings
        if len(text) < 2 or len(text) > 100:
            return ""
        
        return text
    
    def extract_manufacturer(self, model_text):
        """Try to extract manufacturer from model text."""
        if not model_text:
            return ""
        
        # Known manufacturers
        manufacturers = [
            # Lighting
            "ETC", "Martin", "Robe", "Chauvet", "Elation", "Clay Paky", "High End", 
            "Vari-Lite", "Ayrton", "GLP", "Philips", "Osram", "Strand",
            # Sound
            "L-Acoustics", "d&b audiotechnik", "Meyer Sound", "JBL", "Yamaha", 
            "Shure", "Sennheiser", "DPA", "Audio-Technica", "Neumann", "AKG",
            # Video
            "Christie", "Barco", "Epson", "Sony", "Panasonic", "Samsung", 
            "LG", "NEC", "Sharp", "Mitsubishi"
        ]
        
        # Check for exact manufacturer matches at the beginning
        for manufacturer in manufacturers:
            pattern = r'^' + re.escape(manufacturer) + r'\b'
            if re.search(pattern, model_text, re.IGNORECASE):
                return manufacturer
        
        # Try to extract manufacturer from common patterns
        patterns = [
            r'^([A-Z][a-zA-Z\s&-]+?)\s+[A-Z0-9\-]+',  # Brand followed by model number
            r'^([A-Z][a-zA-Z\s&-]{2,15})\s+'  # Capitalized words at the beginning
        ]
        
        for pattern in patterns:
            match = re.search(pattern, model_text)
            if match:
                potential_manufacturer = match.group(1).strip()
                # Validate the extracted manufacturer
                if 2 < len(potential_manufacturer) < 20 and not potential_manufacturer.isdigit():
                    return potential_manufacturer
        
        return ""
    
    def extract_technical_specs(self, text):
        """Extract technical specifications from equipment text."""
        specs = {}
        
        # Power specifications
        power_match = re.search(r'(\d+)\s*[wW](?:att)?', text)
        if power_match:
            specs['power'] = power_match.group(1) + 'W'
        
        # DMX channels for lighting
        dmx_match = re.search(r'(\d+)\s*(?:ch|channel|dmx)', text, re.IGNORECASE)
        if dmx_match:
            specs['dmx_channels'] = dmx_match.group(1)
        
        # Frequency response for sound
        freq_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:Hz|kHz)\s*[-–]\s*(\d+(?:\.\d+)?)\s*(?:Hz|kHz)', text, re.IGNORECASE)
        if freq_match:
            specs['frequency_response'] = f"{freq_match.group(1)}-{freq_match.group(2)} Hz"
        
        # Resolution for video
        res_match = re.search(r'(\d+)\s*[x×]\s*(\d+)', text)
        if res_match and int(res_match.group(1)) > 100 and int(res_match.group(2)) > 100:
            specs['resolution'] = f"{res_match.group(1)}x{res_match.group(2)}"
        
        return specs
    
    def process_venue_pdf(self, pdf_path):
        """Process a venue PDF and extract all equipment information."""
        print(f"  📄 Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            print(f"  ❌ Could not extract text from PDF")
            return None
        
        print(f"  🏢 Identifying venue name...")
        venue_name = self.identify_venue_name(pdf_path, text)
        
        print(f"  🔍 Extracting equipment data...")
        equipment_items = self.extract_equipment_from_text(text)
        
        if not equipment_items:
            print(f"  ⚠️  No equipment items found")
            return None
        
        # Group equipment by type
        equipment_by_type = {
            'lighting': [],
            'sound': [],
            'video': [],
            'other': []
        }
        
        for item in equipment_items:
            eq_type = item.get('equipment_type', 'other')
            equipment_by_type[eq_type].append(item)
        
        venue_data = {
            'venue_name': venue_name,
            'pdf_source': str(pdf_path),
            'equipment': equipment_items,
            'equipment_by_type': equipment_by_type,
            'total_items': len(equipment_items)
        }
        
        print(f"  ✅ Extracted {len(equipment_items)} equipment items")
        for eq_type, items in equipment_by_type.items():
            if items:
                print(f"     {eq_type.capitalize()}: {len(items)} items")
        
        return venue_data