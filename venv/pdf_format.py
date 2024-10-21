from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from dotenv import load_dotenv
import os
import random
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Access environment variables

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv('HF_TOKEN')

user_folder = os.path.expanduser('~')
pdf_path = os.path.join(user_folder, 'Downloads', 'RSall5unit.pdf')
# print(pdf_path)

loader = PyMuPDFLoader(pdf_path)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
docs = text_splitter.split_documents(documents)
# print(len(docs))

embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db = Chroma.from_documents(docs, embedding_function)

random_int = random.randint(1, 1000)
# print(random_int)

persist_directory = os.path.join(user_folder, "Embeddings", f"chroma_db{random_int}")

os.makedirs(persist_directory, exist_ok=True)


db2 = Chroma.from_documents(docs, embedding_function, persist_directory=persist_directory)

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('models/gemini-1.5-flash')
# prompt = 'cosine similarity'

def generate_res(prompt):

    db3 = Chroma(persist_directory=persist_directory, embedding_function=embedding_function)

    result2 = db3.similarity_search_with_score(prompt,k=2)
    # result2

    for i in result2:
      context = ""
      context +=i[0].page_content
      # print(context)
    # nothin = ''

    response = model.generate_content([prompt, f"Based on the context :{context}"])
    return response.text