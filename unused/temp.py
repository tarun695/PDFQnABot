from langchain_community.llms import Ollama

llm = Ollama(model="llama3")

response = llm.invoke("What is llm")
print(response)

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import PyPDFDirectoryLoader


loader = PyPDFDirectoryLoader("pdfs")
docs = loader.load()
len(docs)

print(docs[1])

from langchain_community.embeddings import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="llama3")

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pickle

text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

with open("vector", "wb") as f:
    pickle.dump(vector, f)

from langchain_core.prompts import ChatPromptTemplate

from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

retriever = vector.as_retriever()

# First we need a prompt that we can pass into an LLM to generate this search query

prompt = ChatPromptTemplate.from_template(
    """ 
    
     A set of documents related to pharmaceuticals and drug interactions is provided.
     Your task is to extract information from these documents to accurately respond
     to inquiries about drug effects, interactions, regulations, and other related topics.
     Initially, search the document to find precise answers.
     If the document does not contain the information or if the query requires additional context,
     use your pre-trained knowledge to provide the most accurate response possible.
     Note that the documents might contain complex medical terminology and data that requires careful interpretation.
     When answering, ensure the response is simplified for general understanding while maintaining medical accuracy.
     If a query pertains to adverse effects or safety guidelines and the document is inconclusive, prioritize safety in your response.

<context>
{context}
</context>

Question: {input}"""
)

document_chain = create_stuff_documents_chain(llm, prompt)
# retriever_chain = create_history_aware_retriever(llm, retriever, prompt)

from langchain.chains import create_retrieval_chain
import pickle

with open("vector", "rb") as f:
    vector = pickle.load(f)

retriever = vector.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

response = retrieval_chain.invoke(
    {
        "input": """" How is the drug interacting with the biological system at the site of interaction ?"""
    }
)
print(response["answer"])
