import asyncio
import json
import os
from pathlib import Path

import aiohttp
import structlog
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, FSInputFile
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

from app.url import Url

logger = structlog.get_logger(__name__)

API_TOKEN = os.environ['API_TOKEN']

router = Router()
dp = Dispatcher()
dp.include_router(router)


class CreatingUserStates(StatesGroup):
    waiting_for_username = State()


class GettingUserStates(StatesGroup):
    waiting_for_user_id = State()


async def main() -> None:
    bot = Bot(API_TOKEN)
    logger.info('bot probably started')
    await dp.start_polling(bot)


@router.message(CommandStart())
async def welcome(message: Message) -> None:
    logger.info('sending welcome message')
    await message.answer_photo(FSInputFile('./images/kenobi.png'))
    logger.info('welcome message sent')


@router.message(Command('create_user'))
async def create_user(message: Message, state: FSMContext) -> None:
    logger.info('create_user: starting command')

    await state.set_state(CreatingUserStates.waiting_for_username)
    await message.answer('Please enter user_name')


@router.message(
    CreatingUserStates.waiting_for_username,
)
async def username_chosen(message: Message, state: FSMContext) -> None:
    logger.info('username chosen')

    create_user_name = message.text
    async with aiohttp.request(
            method='post',
            url=str(Url(endpoint=f'tasks/users/')),
            data={'name': create_user_name},
    ) as response:
        json_response = await response.json()
        created_user_id = json_response['id']

    await message.answer(f'user_id: {created_user_id}')
    await state.clear()
    logger.info(f'user {create_user_name} has been created')


@router.message(Command('get_user'))
async def get_user(message: Message, state: FSMContext) -> None:
    logger.info('starting command', command='get_user')
    await state.set_state(GettingUserStates.waiting_for_user_id)
    await message.answer('Please enter user_id')


@router.message(GettingUserStates.waiting_for_user_id)
async def user_id_chosen(message: Message, state: FSMContext) -> None:
    user_id = message.text
    logger.info('Getting user', user_id=user_id)

    async with aiohttp.request(
            method='get',
            url=str(Url(endpoint=f'tasks/users/{user_id}'))
    ) as response:
        user = await response.json()
        logger.info('Got user', user_id=user_id)

    await message.answer(
        ('```json\n'
         f'{json.dumps(user)}\n'
         '```'),
        parse_mode='Markdown'
    )
    await state.clear()


if __name__ == '__main__':
    asyncio.run(main())
