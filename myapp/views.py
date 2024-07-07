# myapp/views.py
from django.shortcuts import render

# from transformers import PreTrainedTokenizerFast, GPT1LMHeadModel, GPT2TokenizerFast, GPT2Tokenizer
import os
from langchain.chains import create_retrieval_chain
import pickle
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
from django.conf import settings


def my_view(request):
    output_str = ""
    if request.method == "POST":
        print("Posting.....")
        input_str = request.POST.get("input_str", "")
        print("------------------------")
        print(input_str)
        print("------------------------")
        output_str = generate_text(input_str)
    return render(request, "index.html", {"output_str": output_str})


def generate_text(user_query):
    file_path = os.path.join(settings.BASE_DIR, "vector")
    # print()
    # print(os.path.join(settings.BASE_DIR, "vector"))
    # print()
    with open(file_path, "rb") as f:
        vector = pickle.load(f)

    retriever = vector.as_retriever()

    # retriever = vector.as_retriever()

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

    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    response = retrieval_chain.invoke({"input": f"""" {user_query}"""})
    print(response["answer"])

    return response["answer"]
