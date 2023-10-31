from langchain.document_loaders import PyPDFLoader # for loading the pdf
from langchain.embeddings import OpenAIEmbeddings # for creating embeddings
from langchain.vectorstores import Chroma # for the vectorization part
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import ChatVectorDBChain # for chatting with the pdf

from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from langchain.chat_models import ChatOpenAI

pdf_path = "./test.pdf"
loader = PyPDFLoader(pdf_path)
pages = loader.load_and_split()

embeddings = OpenAIEmbeddings()
vectordb = Chroma.from_documents(pages, embedding=embeddings,
                                        persist_directory=".")
vectordb.persist()

pdf_qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.9, model_name="gpt-3.5-turbo-16k"),
                                    vectordb, return_source_documents=True)

query = "What is the purchase price"
result = pdf_qa({"question": query, "chat_history": ""})
print("Answer:")
print(result["answer"])