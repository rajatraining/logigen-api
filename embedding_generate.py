import os

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv(".env")

if not os.environ.get("AZURE_OPENAI_API_KEY"):
    raise ValueError(
        "AZURE_OPENAI_API_KEY key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_API_VERSION"):
    raise ValueError(
        "AZURE_OPENAI_API_VERSION key not found in environment variables.")

if not os.environ.get("AZURE_OPENAI_DEPLOYMENT"):
    raise ValueError(
        "AZURE_OPENAI_DEPLOYMENT key not found in environment variables.")

def create_vector_database(txt_path):
    loader = TextLoader(txt_path)

    docs = loader.load()

    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, separators=["\n","\n\n"], chunk_overlap=200
    ).split_documents(docs)

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
        openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
    )
    db = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )
    db.save_local("./faiss-db")

if __name__ == "__main__":
    create_vector_database("./sample_logs/app_log.txt")