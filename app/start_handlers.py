import os
from pathlib import Path

import structlog
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, BotCommand

logger = structlog.get_logger(__name__)

start_router = Router()
bot = Bot(os.environ['API_TOKEN'])


@start_router.message(CommandStart())
async def welcome(message: Message, state: FSMContext, bot: Bot) -> None:
    await state.clear()

    logger.info('sending welcome message')
    await message.answer_photo(FSInputFile(Path(__file__).resolve().parent / 'images' / 'kenobi.png'))
    logger.info('welcome message sent')

    commands = await bot.get_my_commands()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=f"/{cmd.command}") for cmd in commands]
        ],
        resize_keyboard=True
    )

    await message.answer("Выберите команду:", reply_markup=keyboard)


async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Список команд"),
        BotCommand(command="create_user", description="Создать пользователя"),
        BotCommand(command="get_user", description="Получить пользователя"),
        BotCommand(command="create_task", description="Создать задачу"),
        BotCommand(command="get_task", description="Получить задачу"),
        BotCommand(command="create_comment", description="Получить комментарий"),
        BotCommand(command="get_comment", description="Получить комментарий"),
    ]
    await bot.set_my_commands(commands)
