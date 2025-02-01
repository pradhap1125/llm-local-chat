from flask import jsonify
from pdfminer.high_level import extract_text
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
import os
import glob


# Load LLaMA model and tokenizer
model = Ollama(model="llama3")
#model = Ollama(model="deepseek-r1")
# Generate embeddings
#embedding_model = OllamaEmbeddings(model="nomic-embed-text", show_progress=True)
embedding_model = OllamaEmbeddings(model="paraphrase-multilingual", show_progress=True)
local_model_enabled= False
chat_history = []
chat_messages = []

# Load PDF and extract text
def extract_text_from_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text

def clear_chat():
    global chat_history
    chat_history = []
    global chat_messages
    chat_messages = []

# Load your PDF
def load_data(current_directory):
    pdf_files = glob.glob(os.path.join(current_directory, "*.pdf"))
    texts=[]
    for pdf in pdf_files:
        text = extract_text_from_pdf(os.path.abspath(pdf))
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=256, chunk_overlap=10)
        texts.extend(text_splitter.split_text(text))

    # Create a documents
    documents = [Document(page_content=text) for text in texts]

    # Store texts with their embeddings in FAISS vector store
    faiss_vector_store = FAISS.from_documents(documents, embedding_model)
    faiss_vector_store.save_local("test_local")

def rag_query(query):

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise. If the user greets you, you should ignore the context and greet back. "
        "\n\n"
        "{context}"
    )

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    retrived_vector_store = FAISS.load_local("test_local", embedding_model, allow_dangerous_deserialization=True)
    retriever = retrived_vector_store.as_retriever()

    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    ai_msg_1 = rag_chain.invoke({"input": query, "chat_history": chat_history})
    chat_history.extend([HumanMessage(content=query), AIMessage(ai_msg_1["answer"])])
    chat_messages.append({"sender": "User", "message": query})
    chat_messages.append({"sender": "Bot", "message": ai_msg_1['answer']})
    response = jsonify(chat_messages)
    return response

def process_pdf(file):
    file.save(file.filename)
    current_directory = os.getcwd()
    load_data(current_directory)
    return jsonify(message="File uploaded!")
