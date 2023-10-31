import PyPDF2
import re

# Define a function to extract information from the PDF
def extract_info(pdf_path):
    # Open the PDF file
    pdf_file = open(pdf_path, 'rb')
    
    # Create a PDF reader object
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    
    # Initialize variables to store extracted information
    property_info = {}
    
    # Iterate through each page of the PDF
    for page_num in range(pdf_reader.numPages):
        # Extract text from the current page
        page = pdf_reader.getPage(page_num)
        page_text = page.extractText()
        
        # Use regular expressions to extract specific information
        property_name_match = re.search(r'Property Name\s+([^\n]+)', page_text)
        if property_name_match:
            property_info['Property Name'] = property_name_match.group(1)
        
        # Add more regex patterns to extract other information (e.g., Purchase Price, Number of Units, etc.)
        
    # Close the PDF file
    pdf_file.close()
    
    # Print the extracted information
    for key, value in property_info.items():
        print(f"{key}: {value}")

# Specify the path to your offering memorandum PDF
pdf_path = 'memorandum.pdf'

# Call the extract_info function
extract_info(pdf_path)