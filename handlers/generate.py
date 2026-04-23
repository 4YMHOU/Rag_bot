from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from services.llm_service import llm_service

router = Router()

@router.message(Command("generate"))
async def cmd_generate(message: Message, command: CommandObject):
    prompt = command.args
    if not prompt:
        await message.answer("Введите текст для генерации. Пример: /generate Шахматы это")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    answer = llm_service.generate(prompt)
    await message.answer(answer)