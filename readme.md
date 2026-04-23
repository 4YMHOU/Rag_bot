# Отчёт о разработке RAG-бота для Telegram

**Название проекта:** RAG-bot  
**Стек:** Python, aiogram 3, ChromaDB, Sentence-Transformers, Ollama (llama3.2)  
**Репозиторий:** https://github.com/4YMHOU/Rag_bot
**Автор:** 4YMHOU

---

## 1. Описание проекта

Бот для Telegram, реализующий **RAG (Retrieval-Augmented Generation)** — генерацию ответов на основе пользовательского запроса и документов, хранящихся в векторной базе данных. Пользователь может добавлять знания через команду `/add`, искать похожие фрагменты (`/search`), получать обычную генерацию (`/generate`) или генерацию с подкреплением из базы (`/rag`).

Проект демонстрирует разницу между "чистой" LLM (галлюцинации, неточности) и RAG-подходом (точность, опора на факты).

---

## 2. Структура проекта

```
rag_bot/
├── .env                      # BOT_TOKEN=
├── requirements.txt          # зависимости
├── bot.py                    # точка входа, запуск polling
├── config.py                 # чтение переменных окружения
├── handlers/                 # обработчики команд Telegram
│   ├── __init__.py           
│   ├── start.py              # /start, /help
│   ├── add.py                # /add <текст>
│   ├── get_all.py            # /get_all
│   ├── search.py             # /search <запрос>
│   ├── generate.py           # /generate <запрос>
│   └── rag.py                # /rag <запрос>
├── services/                 
│   ├── __init__.py
│   ├── vector_db.py          # обёртка над ChromaDB
│   └── llm_service.py        # обёртка над Ollama API
├── utils/                    
│   ├── __init__.py
│   └── logger.py             # настройка логирования
└── data/                     
    └── chroma_db/            # Хранилище ChromaDB
```

---

## 3. Описание ключевого кода

### 3.1 `bot.py` — запуск бота

```python
import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import routers

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    for router in routers:
        dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.2 `config.py` — загрузка настроек

```python
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHROMA_DB_PATH = "./data/chroma_db"
COLLECTION_NAME = "my_notes"
EMBEDDING_MODEL_NAME = "ai-forever/ru-en-RoSBERTa"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"
```

**Описание параметров:**

| Параметр | Назначение |
|----------|------------|
| `BOT_TOKEN` | Токен для доступа к Telegram API. Без него бот не сможет авторизоваться. |
| `CHROMA_DB_PATH` | Папка, где ChromaDB сохраняет коллекции и эмбеддинги на диск. Указывается относительно корня проекта. |
| `COLLECTION_NAME` | Имя коллекции внутри БД. Позволяет изолировать данные разных проектов. |
| `EMBEDDING_MODEL_NAME` | Имя модели из HuggingFace (или локальной) для расчёта эмбеддингов. Определяет качество поиска. |
| `OLLAMA_URL` | Адрес, по которому Ollama принимает запросы на генерацию. По умолчанию — `http://localhost:11434`. |
| `OLLAMA_MODEL` | Имя модели внутри Ollama. Должна быть загружена через `ollama pull`. |

### 3.3 `services/vector_db.py` — работа с векторной БД

```python
import chromadb
from chromadb.utils import embedding_functions
import uuid
from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME

class VectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        )
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn
        )

    def add_document(self, text: str, metadata: dict = None) -> str:
        doc_id = str(uuid.uuid4())
        self.collection.add(documents=[text], metadatas=[metadata], ids=[doc_id])
        return doc_id

    def search(self, query: str, n_results: int = 3) -> list:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results.get('documents', [[]])[0]
```

### 3.4 `services/llm_service.py` — вызов Ollama

```python
import requests
from config import OLLAMA_URL, OLLAMA_MODEL

class LLMService:
    def generate(self, prompt: str) -> str:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 256}
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return response.json()['response'].strip()

    def generate_with_context(self, query: str, context_docs: list) -> str:
        if not context_docs:
            return "В моей базе знаний нет информации по этому вопросу."
        context = "\n".join(context_docs)
        prompt = f"""Ответь на вопрос, используя ТОЛЬКО предоставленный контекст.
Если в контексте нет ответа, скажи "В моей базе знаний нет информации по этому вопросу".

Контекст:
{context}

Вопрос: {query}
Ответ:"""
        return self.generate(prompt)
```

### 3.5 Обработчики команд

#### `/add` — добавление документа

```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from services.vector_db import vector_db

router = Router()

@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject):
    text = command.args
    if not text:
        await message.answer("Что добавляем? Пример: /add Шахматы — это...")
        return
    vector_db.add_document(text)
    await message.answer("Данные успешно добавлены в БД!")
```

#### `/rag` — RAG-ответ

```python
@router.message(Command("rag"))
async def cmd_rag(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Введи запрос. Пример: /rag Что такое Python?")
        return
    docs = vector_db.search(query, n_results=3)
    if not docs:
        await message.answer("В базе знаний нет информации.")
        return
    answer = llm_service.generate_with_context(query, docs)
    await message.answer(f"Ответ на основе данных из БД:\n\n{answer}")
```

---

## 4. Модель LLM

**Модель:** `llama3.2` (инструктивная) – легковесная, работает на русском и английском.  
**Запуск:** через локальный Ollama (порт 11434).  
**Параметры вызова:**
```json
{
  "model": "llama3.2",
  "prompt": "...",
  "stream": false,
  "options": {"temperature": 0.7, "num_predict": 256}
}
```
- `temperature 0.7` – баланс между креативностью и точностью.  
- `num_predict 256` – ограничение длины ответа.  
- `stream: false` – ответ приходит целиком.

---

## 5. Векторная база данных

**Система:** ChromaDB (persistent-режим)  
**Эмбеддер:** `sentence-transformers/ai-forever/ru-en-RoSBERTa`  
**Размерность эмбеддингов:** 768  
**Количество возвращаемых документов в RAG:** 1  

При добавлении документа через `/add` он преобразуется в эмбеддинг и сохраняется вместе с уникальным ID. При поиске запрос также эмбеддится, и находятся наиболее семантически близкие фрагменты.

---

## 6. Промт для RAG

```python
prompt = f"""Ответь на вопрос, используя ТОЛЬКО предоставленный контекст.
Если в контексте нет ответа, скажи "В моей базе знаний нет информации по этому вопросу".

Контекст:
{context}

Вопрос: {query}
Ответ:"""
```

---

## 7. Сравнение: ответ без БД → с БД

### Без базы данных – команда `/generate Расскажи про python`

> Пайтон (Python) — это высокий nivel язык программирования, разработанный в начале 90-х годов для написания динамических web-страниц... создатель Гидеон Эриксон...

**Проблемы:** фактические ошибки, странная лексика, галлюцинации.

### С базой данных – команда `/rag Что такое Python`

> Python - высокоуровневый язык программирования общего назначения с динамической строгой типизацией и автоматическим управлением памятью.

**Точный ответ**, потому что ранее в БД был добавлен правильный текст.

---

## 8. Вывод

1. **Чистая LLM** склонна к выдумыванию фактов.  
2. **RAG** кардинально повышает достоверность ответов.  
3. Качество RAG зависит от полноты базы знаний.  
4. Проект легко масштабируется (смена эмбеддера, LLM).  
5. Рекомендуется увеличить `n_results` до 5–10 и добавить reranking.

**Итог:** RAG-бот успешно решает задачу фактологического ответа на базе пользовательских данных.

---

## 9. Как запустить

```bash
git clone <repo>
cd rag_bot
pip install -r requirements.txt
ollama run llama3.2   # в отдельном терминале
echo "BOT_TOKEN=ваш_токен" > .env
python bot.py
```

---

## 📎 Приложение: `requirements.txt`

```
aiogram==3.13.1
chromadb==0.5.23
sentence-transformers==3.1.1
requests==2.32.3
python-dotenv==1.0.1
pydantic==2.8.2
pydantic-settings==2.5.2
```
 
**Дата:** апрель 2026

---
