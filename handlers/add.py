from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from services.vector_db import vector_db
from utils.logger import logger

router = Router()

@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject):
    text_to_add = command.args
    if not text_to_add:
        await message.answer("Что добавляем? Пример: /add Шахматы — это...")
        return

    vector_db.add_document(text_to_add)
    await message.answer("Данные успешно добавлены в БД!")
    logger.info(f"Пользователь {message.from_user.id} добавил документ")