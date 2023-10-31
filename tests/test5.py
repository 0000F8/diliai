import spacy
import PyPDF2
import re

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

# Function to extract information from text using NER
def extract_info_with_ner(text):
    property_info = {}
    
    doc = nlp(text)
    
    for ent in doc.ents:

        if ent.label_ == "MONEY":
            if "Purchase Price" not in property_info:
                property_info["Purchase Price"] = ent.text
                print(f"Ent: {ent}, Entity: {ent.label_}, Text: {ent.text}")
        elif ent.label_ == "CARDINAL":
            if "Number of Units" not in property_info:
                property_info["Number of Units"] = ent.text
                print(f"Ent: {ent}, Entity: {ent.label_}, Text: {ent.text}")
        # Add more conditions for other types of information (e.g., sq. ft., rent, occupancy rate, etc.)
    
    return property_info

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

# PDF file path (replace with your file path)
pdf_path = 'memorandum.pdf'

# Extract text from the PDF
pdf_text = extract_text_from_pdf(pdf_path)

text_segments = split_text(pdf_text)
extracted_info = {}

# Extract information from the text using NER
for segment in text_segments:
    segment_info = extract_info_with_ner(segment)
    extracted_info.update(segment_info)

# Print the extracted information
for key, value in extracted_info.items():
    print(f"{key}: {value}")
