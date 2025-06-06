import asyncio
import os

import structlog
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

logger = structlog.get_logger(__name__)

load_dotenv()
API_TOKEN = os.environ['API_TOKEN']  # use venv here

router = Router()


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    bot = Bot(API_TOKEN)
    logger.info('hoping that bot started')
    await dp.start_polling(bot)


@router.message(CommandStart())
async def welcome(message: Message) -> None:
    logger.info('sending welcome message')
    await message.answer_photo(FSInputFile('./images/kenobi.png'))
    logger.info('welcome message sent')


if __name__ == '__main__':
    asyncio.run(main())
