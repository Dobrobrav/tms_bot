import json

import aiohttp
import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from url import Url
from utils import make_pretty_json_in_telegram

logger = structlog.get_logger(__name__)
user_router = Router()


class CreatingUserStates(StatesGroup):
    waiting_for_username = State()


class GettingUserStates(StatesGroup):
    waiting_for_user_id = State()


@user_router.message(Command('create_user'))
async def create_user(message: Message, state: FSMContext) -> None:
    logger.info('create_user: starting command')

    await state.set_state(CreatingUserStates.waiting_for_username)
    await message.answer('Please enter user_name')


@user_router.message(CreatingUserStates.waiting_for_username)
async def username_chosen(message: Message, state: FSMContext) -> None:
    logger.info('username chosen')

    create_user_name = message.text
    async with aiohttp.request(
            method='post',
            url=str(Url(endpoint=f'tasks/users/')),
            data={'name': create_user_name},
    ) as response:
        if response.status == 201:
            json_response = await response.json()
            created_user_id = json_response['id']
            await message.answer(f'user_id: {created_user_id}')
            logger.info(f'user {create_user_name} has been created')
        else:
            response_text = await response.text()
            await message.answer(response_text)

        await state.clear()


@user_router.message(Command('get_user'))
async def get_user(message: Message, state: FSMContext) -> None:
    logger.info('starting command', command='get_user')
    await state.set_state(GettingUserStates.waiting_for_user_id)
    await message.answer('Please enter user_id')


@user_router.message(GettingUserStates.waiting_for_user_id)
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
        make_pretty_json_in_telegram(json.dumps(user)),
        parse_mode='Markdown'
    )
    await state.clear()
