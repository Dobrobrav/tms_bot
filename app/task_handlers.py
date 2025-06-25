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
from utils import make_pretty_json_in_telegram

logger = structlog.get_logger(__name__)
task_router = Router()


class CreatingTaskStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_reporter_id = State()
    waiting_for_assignee_id = State()
    waiting_for_related_task_ids = State()


@task_router.message(Command('create_task'))
async def create_task(message: Message, state: FSMContext) -> None:
    await state.clear()

    logger.info('start creating task')
    await state.set_state(CreatingTaskStates.waiting_for_title)
    await message.answer('Enter task title')
    logger.info('asked for task title')


@task_router.message(CreatingTaskStates.waiting_for_title)
async def title_chosen(message: Message, state: FSMContext) -> None:
    title = message.text.strip()
    logger.info('task title has been chosen', title=title)
    await state.update_data(title=title)
    await state.set_state(CreatingTaskStates.waiting_for_description)
    await message.answer('Enter task description')
    logger.info('asked for task description')


@task_router.message(CreatingTaskStates.waiting_for_description)
async def description_chosen(message: Message, state: FSMContext) -> None:
    description = None if message.text.strip() == '-' else message.text.strip()
    logger.info(
        'task description has been chosen' if description else 'task description was omitted',
        description=description,
    )
    await state.update_data(description=description)
    await state.set_state(CreatingTaskStates.waiting_for_reporter_id)
    await message.answer('Enter reporter id')
    logger.info('asked for task reporter_id')


@task_router.message(CreatingTaskStates.waiting_for_reporter_id)
async def reporter_id_chosen(message: Message, state: FSMContext) -> None:
    reporter_id = int(message.text.strip())
    logger.info('task reporter_id has been chosen', reporter_id=reporter_id)
    await state.update_data(reporter_id=reporter_id)
    await state.set_state(CreatingTaskStates.waiting_for_assignee_id)
    await message.answer('Enter assignee id')
    logger.info('asked for task assignee_id')


@task_router.message(CreatingTaskStates.waiting_for_assignee_id)
async def assignee_id_chosen(message: Message, state: FSMContext) -> None:
    assignee_id = None if message.text.strip() == '-' else message.text.strip()
    logger.info(
        'task assignee_id has been chosen' if assignee_id else 'task assignee_id was omitted',
        assignee_id=assignee_id,
    )
    await state.update_data(assignee_id=assignee_id)
    await state.set_state(CreatingTaskStates.waiting_for_related_task_ids)
    await message.answer('Enter related task ids')
    logger.info('asked for task related_task_ids. Format: <task_id_1>, <task_id_2>, ..., <task_id_n>')


@task_router.message(CreatingTaskStates.waiting_for_related_task_ids)
async def related_task_ids_chosen(message: Message, state: FSMContext) -> None:
    related_task_ids = None if message.text.strip() == '-' else message.text.strip()
    logger.info(
        'task related_task_ids has been chosen' if related_task_ids else 'task related_task_ids was omitted',
        related_task_ids=related_task_ids,
    )
    related_task_ids = await _parce_related_task_ids(related_task_ids)
    await state.update_data(related_task_ids=related_task_ids)

    task_data = await state.get_data()
    async with aiohttp.request(
            'POST',
            url=str(Url(endpoint='tasks/tasks/')),
            json=task_data,
    ) as response:
        response_json = await response.json()

        if response.status == 200:
            created_task_id = response_json
            await message.answer(f'created task id: {created_task_id}')
        else:
            await message.answer(
                make_pretty_json_in_telegram(json.dumps(response_json)),
                parse_mode='Markdown',
            )

    await state.clear()


async def _parce_related_task_ids(related_task_ids):
    return related_task_ids.split(', ') if related_task_ids else []


class GettingTaskStates(StatesGroup):
    waiting_for_task_id = State()


@task_router.message(Command('get_task'))
async def get_task(message: Message, state: FSMContext) -> None:
    await state.clear()

    logger.info('starting command', command='get_task')
    await state.set_state(GettingTaskStates.waiting_for_task_id)
    await message.answer('Enter task id')


@task_router.message(GettingTaskStates.waiting_for_task_id)
async def task_id_chosen(message: Message, state: FSMContext) -> None:
    task_id = int(message.text.strip())

    logger.info('getting task', task_id=task_id)

    async with aiohttp.request(
            'get',
            url=str(Url(endpoint=f'tasks/tasks/{task_id}')),
    ) as response:
        if response.status == 200:
            json_data = await response.json()
            await message.answer(utils.make_pretty_json_in_telegram(json_data), parse_mode='Markdown')
        else:
            response_text = await response.text()
            await message.answer(response_text)

        await state.clear()
