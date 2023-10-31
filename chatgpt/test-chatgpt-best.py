import openai
import pdfplumber
import os
import sys
import tabula
import pandas as pd
import re
import json

# Retrieve the API key from the local environment
api_key = os.environ.get("OPENAI_API_KEY")

if api_key is None:
    print("API key not found in the environment. Set the OPENAI_API_KEY variable.")
    exit()

# Initialize the OpenAI API client
openai.api_key = api_key

# 1800 is good
model_max_length = 19000

details = {
    "Property Name": "",
    "Purchase Price": "",
    "Number of Units": "",
    "Price per Unit": "",
    "Average Unit Sq. Ft.": "",
    "Total Rentable Sq. Ft.": "",
    "Average Monthly Rent": "",
    "Average Rent / Sq. Ft.": "",
    "Occupancy Rate": "",
    "Sponsor": "",
    "Zip Code": "",
}

def split_text_by_length(text, max_length):
    """
    Split a text into segments of a specified maximum character length.

    Args:
        text (str): The input text to split.
        max_length (int): The maximum character length for each segment.

    Returns:
        list of str: A list of text segments.
    """
    segments = []
    current_segment = ""
    
    for char in text:
        if len(current_segment) < max_length:
            current_segment += char
        else:
            segments.append(current_segment)
            current_segment = char
    
    if current_segment:
        segments.append(current_segment)
    
    return segments

# Function to extract text from a PDF using pdfplumber
def extract_text_from_pdf(pdf_file_path):
    extracted_text = ""
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            # Extract text from each page and concatenate it
            page_text = page.extract_text()
            extracted_text += page_text
    return extracted_text

# Function to extract tabular data from a PDF using tabula
def extract_tabular_data_from_pdf(pdf_file_path):
    # Use tabula to extract tables from the PDF
    tables = tabula.read_pdf(pdf_file_path, pages='all')
    
    # Process and format the extracted tables (you can customize this)
    formatted_tables = []
    for table in tables:
        formatted_table = table.fillna("")  # Replace NaN values with empty strings
        formatted_tables.append(formatted_table)
    
    return formatted_tables

# Function to use the LLM for data extraction
def extract_data_from_text(text):

    # prompt = f"Extract and return ONLY 'Property Name', 'Purchase Price', 'Number of Units', 'Price per Unit', 'Average Unit Sq. Ft.', 'Total Rentable Sq. Ft.', 'Average Monthly Rent', 'Average Rent / Sq. Ft.', 'Occupancy Rate', 'Sponsor', and 'Zip Code' from the following text:\n\n{text}"
    system_prompt = f"""
        You will be provided with an offering memorandum.
        Do not confuse multiple properties. You may have to infer some data such as zip code.
        Extract and return the following information ONLY in the same case, and be as succinct as possible, in the format <FIELD>: <VALUE>:

        Property Name
        Purchase Price
        Number of Units
        Price per Unit
        Average Unit Sq. Ft.
        Total Rentable Sq. Ft.
        Average Monthly Rent
        Average Rent / Sq. Ft.
        Occupancy Rate
        Sponsor
        Zip Code
        """

    user_prompt = f"""{text}"""

    #print(prompt)
    #sys.exit(0)

    # Generate a response from the LLM
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",  # You can choose the engine that fits your needs
        messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "system", "content": system_prompt},

            {"role": "user", "content": user_prompt}
        ]
    )
    
    # Extract the LLM-generated text from the response
    generated_text = response.choices[0].message.content
    
    return generated_text

def parse_property_details(property_details_str):
    """
    Parse property details from a formatted string into a dictionary.

    Args:
        property_details_str (str): The input string containing property details.

    Returns:
        dict: A dictionary containing parsed property details.
    """
    parsed_details = {}
    
    # Define regular expressions to extract key-value pairs
    key_value_pattern = r"([^:]+):\s*([^:]+)\n"
    
    # Extract key-value pairs from the input string
    matches = re.findall(key_value_pattern, property_details_str)
    
    for key, value in matches:
        parsed_details[key.strip()] = value.strip()
    
    return parsed_details

def update_property_details(property_details, new_values):
    """
    Update property details with new values.

    Args:
        property_details (dict): A dictionary containing property details.
        new_values (dict): A dictionary containing the new values for specific keys.

    Returns:
        dict: The updated property details.
    """
    skip_pattern = re.compile(r'.*(n/a|not provided|not specified|not mentioned).*', re.IGNORECASE)


    for key, value in new_values.items():
        if key in property_details and not skip_pattern.match(value):
            property_details[key] = value
    return property_details

# Example usage:
pdf_file_path = "test.pdf"
extracted_text_data = extract_text_from_pdf(pdf_file_path)
# tabular_data = extract_tabular_data_from_pdf(pdf_file_path)

# for i, table in enumerate(tabular_data):
#    print(f"Table {i + 1}:")
#    print(table)
#    print("\n")

segments = split_text_by_length(extracted_text_data, model_max_length)

# Use the LLM to extract data from the extracted text
for i, segment in enumerate(segments):
    extracted_data = extract_data_from_text(segment)
    #print(f"🎃 Extracted Data from LLM: {extracted_data}")
    new_details = parse_property_details(extracted_data)
    print(new_details)
    details = update_property_details(details, new_details)

print(json.dumps(details, indent=4))