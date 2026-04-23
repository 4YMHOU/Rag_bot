from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.vector_db import vector_db

router = Router()

@router.message(Command("get_all"))
async def cmd_get_all(message: Message):
    documents = vector_db.get_all_documents()
    if not documents:
        await message.answer("В БД пусто")
        return

    response = "Все мои данные:\n\n"
    for doc in documents:
        response += f"• {doc}\n"
        if len(response) > 3500:
            await message.answer(response)
            response = ""

    if response:
        await message.answer(response)