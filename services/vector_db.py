import chromadb
from chromadb.utils import embedding_functions
import uuid
import os
from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME
from utils.logger import logger

class VectorDB:
    def __init__(self):
        os.makedirs(CHROMA_DB_PATH, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )
        logger.info(f"Подключение к ChromaDB: коллекция '{COLLECTION_NAME}'")

    def add_document(self, text: str, metadata: dict = None) -> str:
        doc_id = str(uuid.uuid4())
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else None,
            ids=[doc_id]
        )
        logger.info(f"Документ добавлен, ID: {doc_id[:8]}...")
        return doc_id

    def search(self, query: str, n_results: int = 3) -> list:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        documents = results.get('documents', [[]])[0]
        logger.info(f"Поиск по запросу '{query}': найдено {len(documents)} документов")
        return documents

    def get_all_documents(self, limit: int = 100) -> list:
        all_docs = self.collection.get(limit=limit)
        documents = all_docs.get('documents', [])
        logger.info(f"Получено {len(documents)} документов из БД")
        return documents


vector_db = VectorDB()