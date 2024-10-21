from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
# from langchain_community.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Access environment variables

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv('HF_TOKEN')

loader = TextLoader("./RSDOC.txt", encoding='utf-8')
documents = loader.load()
# documents[0].page_content

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
# len(docs)

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2") #textembeddingada

db = Chroma.from_documents(docs, embedding_function)


# db2 = Chroma.from_documents(docs, embedding_function, persist_directory='./chroma_db1')
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('models/gemini-1.5-flash')
# prompt = 'cosine similarity'

def generate_res(prompt):

    db3 = Chroma(persist_directory='./chroma_db1', embedding_function=embedding_function)

    result2 = db3.similarity_search_with_score(prompt,k=2)
    # result2

    for i in result2:
      context = ""
      context +=i[0].page_content
      print(context)

    response = model.generate_content([prompt, context])
    return response.text