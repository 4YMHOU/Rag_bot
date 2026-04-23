from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from services.vector_db import vector_db

router = Router()

@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject):
    query = command.args
    if not query:
        await message.answer("Что ищем? Пример: /search шахматы")
        return

    documents = vector_db.search(query, n_results=1)
    if not documents:
        await message.answer("Ничего не найдено.")
        return

    response = "Что-то нашлось:\n\n" + "\n---\n".join(documents)
    await message.answer(response)