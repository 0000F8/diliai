from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader # for loading the pdf
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains.question_answering import load_qa_chain


# This gets us pretty far, but I think context is lost somewhere

pdf_path = "./test.pdf"
loader = PyPDFLoader(pdf_path)
#text_splitter = RecursiveCharacterTextSplitter(chunk_size=16000, chunk_overlap=400) # works ok
text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=10) 
data = loader.load()
texts = text_splitter.split_documents(data)

embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(texts, embeddings)

qa_chain = load_qa_chain(ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0), chain_type="stuff")
qa = RetrievalQA(combine_documents_chain=qa_chain, retriever=docsearch.as_retriever())

## perform search based on the question
query_params = ["Property Name", "Purchase Price", "Number of Units", "Price per Unit", "Average Unit Sq. Ft.", "Total Rentable Sq. Ft.", "Average Monthly Rent", "Average Rent / Sq. Ft.", "Occupancy Rate", "Sponsor", "Zip Code"]

for param in query_params:
  query = f"What is the {param}"
  res = qa.run(query)
  print(res)