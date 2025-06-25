import json

import aiohttp
import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

import utils
from url import Url

logger = structlog.get_logger(__name__)

comment_router = Router()


class CreateCommentStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_user_id = State()
    waiting_for_task_id = State()


@comment_router.message(Command('create_comment'))
async def create_comment(message: Message, state: FSMContext) -> None:
    logger.info('start command', command='create_comment')

    await state.set_state(CreateCommentStates.waiting_for_text)
    await message.answer('Enter comment text')
    logger.info('Asked for comment text')


@comment_router.message(CreateCommentStates.waiting_for_text)
async def text_chosen(message: Message, state: FSMContext) -> None:
    logger.info('message text chosen', text=message.text)

    await state.update_data(text=message.text)
    await state.set_state(CreateCommentStates.waiting_for_user_id)
    await message.answer('Enter user id')

    logger.info('Asked for user id')


@comment_router.message(CreateCommentStates.waiting_for_user_id)
async def user_id_chosen(message: Message, state: FSMContext) -> None:
    user_id = int(message.text)
    logger.info('user id chosen', user_id=user_id)

    await state.update_data(user_id=user_id)
    await state.set_state(CreateCommentStates.waiting_for_task_id)
    await message.answer('Enter task id')

    logger.info('Asked for task id')


@comment_router.message(CreateCommentStates.waiting_for_task_id)
async def task_id_chosen(message: Message, state: FSMContext) -> None:
    task_id = int(message.text)
    logger.info('task id chosen', task_id=task_id)

    await state.update_data(task_id=task_id)
    comment_data = await state.get_data()

    async with aiohttp.request(
            'post',
            url=str(Url(endpoint='tasks/comments/')),
            json=comment_data,
    ) as response:
        if response.status == 201:
            logger.info('comment created', comment=(await response.json()))
            await message.answer(
                utils.make_pretty_json_in_telegram(json.dumps(await response.json())),
                parse_mode='Markdown',
            )
        else:
            await message.answer(await response.text())

        await state.clear()


class GetCommentStates(StatesGroup):
    waiting_for_comment_id = State()


@comment_router.message(Command('get_comment'))
async def get_comment(message: Message, state: FSMContext) -> None:
    logger.info('start command', command='get_comment')

    await state.set_state(GetCommentStates.waiting_for_comment_id)
    await message.answer('Enter comment id')

    logger.info('Asked for comment id')


@comment_router.message(GetCommentStates.waiting_for_comment_id)
async def comment_id_chosen(message: Message, state: FSMContext) -> None:
    comment_id = int(message.text)
    logger.info('comment id chosen', comment_id=comment_id)

    async with aiohttp.request(
            'get',
            url=str(Url(endpoint=f'tasks/comments/{comment_id}')),
    ) as response:
        if response.status == 200:
            comment_json = await response.json()
            logger.info('comment received', comment=comment_json)
            await message.answer(
                utils.make_pretty_json_in_telegram(json.dumps(comment_json)),
                parse_mode='Markdown',
            )
        else:
            logger.info('got non successful response', response=(await response.text()))
            await message.answer(await response.text())

        await state.clear()
