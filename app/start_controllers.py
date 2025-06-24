import structlog
from aiogram.types import Message, FSInputFile

logger = structlog.get_logger(__name__)


async def welcome(message: Message) -> None:
    logger.info('sending welcome message')
    await message.answer_photo(FSInputFile('./images/kenobi.png'))
    logger.info('welcome message sent')
