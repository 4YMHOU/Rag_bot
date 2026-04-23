from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from services.vector_db import vector_db
from services.llm_service import llm_service

router = Router()

@router.message(Command("rag"))
async def cmd_rag(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Введи запрос в RAG. Пример: /rag Сколько фигур в шахматах?")
        return

    documents = vector_db.search(query, n_results=3)
    if not documents:
        await message.answer("В базе знаний не найдено информации по вашему запросу.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    answer = llm_service.generate_with_context(query, documents)
    
    final_response = f"Ответ на основе данных из БД:\n\n{answer}"
    await message.answer(final_response)