from langchain.chains import RetrievalQA
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from langchain.chat_models import ChatOpenAI
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain.chains import create_qa_with_sources_chain


from langchain.document_loaders import PyPDFLoader # for loading the pdf

pdf_path = "./solomonoff.pdf"

loader = PyPDFLoader(pdf_path)
documents = loader.load()

#text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
text_splitter = CharacterTextSplitter(chunk_size=5000, chunk_overlap=300)
texts = text_splitter.split_documents(documents)

for i, text in enumerate(texts):
    text.metadata["source"] = f"{i}-pl"

embeddings = OpenAIEmbeddings()
docsearch = Chroma.from_documents(texts, embeddings, collection_metadata={"hnsw:space": "cosine"})

llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo-16k")

qa_chain = create_qa_with_sources_chain(llm)

doc_prompt = PromptTemplate(
    template="Content: {page_content}\nSource: {source}",
    input_variables=["page_content", "source"],
)

final_qa_chain = StuffDocumentsChain(
    llm_chain=qa_chain,
    document_variable_name="context",
    document_prompt=doc_prompt,
)

retrieval_qa = RetrievalQA(
    retriever=docsearch.as_retriever(), combine_documents_chain=final_qa_chain
)

# query_params = ["Property Name", "Purchase Price", "Number of Units", "Price per Unit", "Average Unit Sq. Ft.", "Total Rentable Sq. Ft.", "Average Monthly Rent", "Average Rent / Sq. Ft.", "Occupancy Rate", "Sponsors", "Zip Code"]
# for param in query_params:
#  print(param)
#  query = f"What is the {param}, return only the found value and no other words"
#  print(retrieval_qa.run(query))

query = f"Name all the other researchers referenced inside the text."
print(retrieval_qa.run(query))