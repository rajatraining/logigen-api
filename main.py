import os

from langchain.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv("/.env") # Enter your .env path here

os.environ["AZURE_OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ.get("AZURE_OPENAI_ENDPOINT")
os.environ["AZURE_OPENAI_API_VERSION"] = os.environ.get("AZURE_OPENAI_API_VERSION")

embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
)

vectorstore_faiss = FAISS.load_local("/faiss-db", embeddings, allow_dangerous_deserialization=True)
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    verbose=False,
    temperature=0.3,
)
PROMPT_TEMPLATE = """You are an AI Assistant. Given the following context:{context}

Answer the following question:
{question}

Assistant:"""

PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE, input_variables=["context", "question"]
)

qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k" : 6 }
    ),
    verbose=False,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
)
question = "" # Enter your question here
response = qa.invoke({"query": question})
result = response["result"]