import openai
import PyPDF2
import os

# split the pdf into pages
# each page will be split and sent to ChatGPT for search
# 

# Set your OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

# Open the PDF file and extract text
with open('test.pdf', 'rb') as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Initialize an empty string to store the extracted text
    pdf_text = ''

    # Extract text from each page
    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        pdf_text += page.extract_text()

# Split the extracted text into manageable chunks (e.g., paragraphs)
text_chunks = pdf_text.split('\n\n')  # Split by empty lines for simplicity

# Initialize variables for conversation context
conversation = []

# Process each text chunk sequentially
for i, text_chunk in enumerate(text_chunks):
    # Construct a message for the current text chunk
    message = {
        "role": "system",
        "content": "You are a helpful assistant."
    }
    message["content"] = text_chunk
    conversation.append(message)
    
    # Check if conversation length exceeds the context size limit
    if len(openai.ChatCompletion.create(model="gpt-3.5-turbo-16k", messages=conversation)['choices'][0]['message']['content']) > 4096:
        # If it exceeds the limit, send the request and start a new conversation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=conversation
        )
        
        # Extract the assistant's response
        assistant_response = response['choices'][0]['message']['content']
        
        # Print the assistant's response
        print(f"Assistant Response for Chunk {i+1}:\n{assistant_response}\n")
        
        # Start a new conversation with a truncated context
        # For example, you can keep only the last message
        conversation = [{"role": "user", "content": assistant_response}]

    
# After processing all chunks, you can ask questions or make requests
question = "What insights can you provide about the entire document?"

# Send the final request for the remaining conversation
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-16k",
    messages=conversation + [{"role": "user", "content": question}]
)

# Extract the assistant's final response
final_response = response['choices'][0]['message']['content']

# Print the final response
print(f"Final Assistant Response:\n{final_response}\n")
