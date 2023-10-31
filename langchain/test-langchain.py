import os
import langchain
import openai
from langchain.vectorstores import FAISS

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

## importing necessary framework
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

from langchain.chat_models import ChatOpenAI



api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = api_key

# load the data
loader = PyPDFLoader('test.pdf')

# the 10k financial report are huge, we will need to split the doc into multiple chunk.
# This text splitter is the recommended one for generic text. It is parameterized by a list of characters. 
# It tries to split on them in order until the chunks are small enough.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=400)
data = loader.load()
texts = text_splitter.split_documents(data)

# view the first chunk

# initialize OpenAIEmbedding
embeddings = OpenAIEmbeddings(model='text-embedding-ada-002')

# use Chroma to create in-memory embedding database from the doc

metadatas = [{"source": str(i)} for i in range(len(texts))]

docsearch = Chroma.from_documents(texts, embeddings) #,  metadatas=metadatas)

## perform search based on the question
query_params = ["Property Name", "Purchase Price", "Number of Units", "Price per Unit", "Average Unit Sq. Ft.", "Total Rentable Sq. Ft.", "Average Monthly Rent", "Average Rent / Sq. Ft.", "Occupancy Rate", "Sponsor", "Zip Code"]

for param in query_params:
  query = f"What is the {param}"
  docs = docsearch.similarity_search(query)

  ## use LLM to get answering
  chain = load_qa_chain(ChatOpenAI(temperature=0.2,model_name='gpt-3.5-turbo-16k'), 
                        chain_type="stuff")
  res = chain.run(input_documents=docs, question=query)
  print(res)



#db2 = Chroma.from_documents(docs, embedding_function, persist_directory="./chroma_db")
