from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет!\nСписок команд: /help.")

@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "Доступные команды:\n"
        "/add &lt;текст&gt; — сохранить новые данные в БД\n"
        "/get_all — вывести список всех сохраненных данных в БД\n"
        "/search &lt;запрос&gt; — найти наиболее похожие данные в БД\n"
        "/generate &lt;проект&gt; — сгенерировать текст\n"
        "/rag &lt;проект&gt; — сгенерировать текст по данным из БД\n"
        "/help — показать это сообщение"
    )
    await message.answer(help_text, parse_mode="HTML")