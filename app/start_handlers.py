import structlog
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from pathlib import Path

logger = structlog.get_logger(__name__)

start_router = Router()


@start_router.message(CommandStart())
async def welcome(message: Message) -> None:
    logger.info('sending welcome message')
    await message.answer_photo(FSInputFile(Path(__file__).resolve().parent / 'images' / 'kenobi.png'))
    logger.info('welcome message sent')
