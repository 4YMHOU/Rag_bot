import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN не установлена!")

CHROMA_DB_PATH = "./data/chroma_db"
COLLECTION_NAME = "my_notes"
EMBEDDING_MODEL_NAME = "ai-forever/ru-en-RoSBERTa"  

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  