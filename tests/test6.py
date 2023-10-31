import PyPDF2
import pdfplumber
import tabula
import re
import spacy

import os

java_home = os.environ.get('JAVA_HOME')
print(f'JAVA_HOME: {java_home}')

# Load the pretrained NER model
nlp = spacy.load("en_core_web_trf")

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_file = open(pdf_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    
    pdf_file.close()
    return text

# Function to split text into smaller segments
def split_text(text, max_length=512):
    segments = []
    current_segment = ""
    
    for paragraph in text.split('\n'):
        if len(current_segment) + len(paragraph) < max_length:
            current_segment += paragraph + '\n'
        else:
            segments.append(current_segment.strip())
            current_segment = paragraph + '\n'
    
    if current_segment:
        segments.append(current_segment.strip())
    
    return segments

# Function to extract information from text using regex
def extract_info_from_text(text):
    property_info = {}
    
    # Define patterns to search for specific information using regex
    patterns = {
        "Property Name": r'Property\s+Name\s*:\s*(.*)',
        "Purchase Price": r'Purchase\s+Price\s*:\s*\$([\d,]+)',
        "Number of Units": r'Number\s+of\s+Units\s*:\s*(\d+)',
        "Price per Unit": r'Price\s+per\s+Unit\s*:\s*\$([\d,]+)',
        "Average Unit Sq. Ft.": r'Average\s+Unit\s+Sq.\s+Ft.\s*:\s*(\d+)',
        "Total Rentable Sq. Ft.": r'Total\s+Rentable\s+Sq.\s+Ft.\s*:\s*([\d,]+)',
        "Average Monthly Rent": r'Average\s+Monthly\s+Rent\s*:\s*\$([\d,]+)',
        "Average Rent / Sq. Ft.": r'Average\s+Rent\s+/ Sq.\s+Ft.\s*:\s*\$([\d,.]+)',
        "Occupancy Rate": r'Occupancy\s+Rate\s*:\s*(\d+\s*%)',
        "Sponsor": r'Sponsor\s*:\s*(.*)',
        "Zip Code": r'Zip\s+Code\s*:\s*(\d+)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            property_info[key] = match.group(1)
    
    return property_info

# Function to extract information from tabular PDFs using tabula
def extract_info_from_tabular_pdf(pdf_path):
    # Use tabula to extract tables from the PDF with automatic detection
    #tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
    tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)

    
    # Process and extract information from each table
    extracted_info_tabular = {}
    for i, table in enumerate(tables):
        for column in table.columns:
            for item in column:
                # Extract information using NER on table text
                entities = extract_info_from_text(item)
                if entities:
                    extracted_info_tabular[f"Table_{i}_Column_{column.name}"] = entities
    
    return extracted_info_tabular

# PDF file path (replace with your file path)
pdf_path = 'test.pdf'

# Extract text from the PDF
pdf_text = extract_text_from_pdf(pdf_path)

# Split text into smaller segments
text_segments = split_text(pdf_text)

# Extract entities from each segment using NER
all_entities = []
for segment in text_segments:
    segment_entities = extract_info_from_text(segment)
    all_entities.extend(segment_entities)

# Extract information from tabular PDFs with automatic detection
extracted_info_tabular = extract_info_from_tabular_pdf(pdf_path)

# Merge information from both sources
merged_info = {**dict(all_entities), **extracted_info_tabular}

# Print the extracted information
for key, value in merged_info.items():
    print(f"{key}: {value}")
