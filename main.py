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

bot = Bot(API_TOKEN)
router = Router()


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)

    logger.info('hoping that bot started')
    await dp.start_polling(bot)


@router.message(CommandStart())
async def welcome(message: Message) -> None:
    logger.info('sending welcome message')
    # with open('./images/kenobi.png', 'r') as img:

    await message.answer_photo(FSInputFile('./images/kenobi.png'))

    # await message.answer('Hello there!')
    logger.info('welcome message sent')


if __name__ == '__main__':
    asyncio.run(main())
