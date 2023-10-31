import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Define a function to extract information from unstructured text
def extract_info(text):
    # Process the text with spaCy
    doc = nlp(text)
    
    # Initialize variables to store extracted information
    property_info = {}
    
    # Iterate through the entities recognized by spaCy
    for ent in doc.ents:
        if ent.label_ == "MONEY":
            # Extract purchase price and other monetary values
            if "Purchase Price" not in property_info:
                property_info["Purchase Price"] = ent.text
            # Add more conditions to extract other numerical values as needed
        
    # Print the extracted information
    for key, value in property_info.items():
        print(f"{key}: {value}")

# Example unstructured text (replace with your own text data)
text_data = """
Property Name: Knol Apartments
The purchase price is $44.5 million, and there are 215 units.
Average unit size is 683 square feet.
"""

# Call the extract_info function
extract_info(text_data)