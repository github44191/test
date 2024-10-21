# from flask import Flask, jsonify, request
# from flask_cors import CORS
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo
from dotenv import load_dotenv
import os
from pdf_format import generate_res
# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process | venv\Scripts\activate 

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

app = FastAPI()
load_dotenv()


origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return "Backend Server using FastAPI"

# @app.get("/items")
# async def read_items():
#     return {"Output": "md" }

# Define a custom type to handle MongoDB's ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type='string')

# Pydantic model to represent a single message-response pair in chat history

class ResponseHistoryItem(BaseModel):
    message: str
    response: str
# Pydantic model to represent the document schema in MongoDB
class History(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    chatHistory: List[ResponseHistoryItem]

    class Config:
        # Configuration for JSON encoding and alias mapping
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
class Message(BaseModel):
    content: str

class SaveHistory(BaseModel):
    responseHistory: List[ResponseHistoryItem]

@app.post("/generate-response")
async def generate_response(message: Message):
    # Replace this with your actual response generation logic
    response_content = generate_res(message.content)
   
    # db.histor.insert_one({
    # 'contentName':message.content,
    # 'content':response_content,
    # 'chatHistory': chat_history_dicts
    # })
    return {"response": response_content}

@app.post("/addHistory")
async def add_history(save_history: SaveHistory):
    chat_history_dicts = [item.model_dump() for item in save_history.responseHistory]
    db.history.insert_one({
    'chatHistory': chat_history_dicts
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)



# uri = f"mongodb+srv://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}@cluster0.s7oe3nd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
uri = "mongodb://localhost:27017/"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.chatHistory
history_collection = db['history']

@app.get("/histories/", response_model=List[History])
async def get_histories():
    histories = history_collection.find({})
    return [History(**history) for history in histories]

# db.create_collection('py')
# app = Flask(__name__)
# CORS(app)  # This will enable CORS for all routes

# @app.route('/')
# def home():
#     return "Hello, Flask!"

# @app.route('/api/data', methods=['GET'])
# def get_data():
#     data = {"Output": output}
#     return jsonify(data)

# @app.route('/api/data', methods=['POST'])
# def post_data():
#     data = request.get_json()
#     return jsonify(data), 201

# if __name__ == '__main__':
#     app.run(debug=True)
