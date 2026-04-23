import requests
import json
from config import OLLAMA_URL, OLLAMA_MODEL
from utils.logger import logger

class LLMService:
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 256  # Ограничиваем длину ответа
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()['response'].strip()
            logger.info(f"LLM сгенерировала ответ длиной {len(result)} символов")
            return result
        except Exception as e:
            logger.error(f"Ошибка при обращении к LLM: {e}")
            return f"Ошибка при обращении к языковой модели: {e}"

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
        logger.info(f"RAG запрос: {query}")
        return self.generate(prompt)

llm_service = LLMService()