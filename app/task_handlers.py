import json
from typing import AsyncGenerator

import aiohttp
import httpx
import structlog
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, File
from aiohttp import StreamReader

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

    logger.info('Asked for task id')


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


class AddingAttachmentStates(StatesGroup):
    waiting_for_task_id = State()
    waiting_for_attachment = State()


@task_router.message(Command('add_attachment_to_task'))
async def add_attachment(message: Message, state: FSMContext) -> None:
    await state.clear()

    logger.info('starting command', command='add_attachment_to_task')

    await state.set_state(AddingAttachmentStates.waiting_for_task_id)
    await message.answer('Enter task id')

    logger.info('Asked for task id')


@task_router.message(AddingAttachmentStates.waiting_for_task_id)
async def add_attachment__task_id_chosen(message: Message, state: FSMContext) -> None:
    task_id = int(message.text)
    logger.info('task id chosen', task_id=task_id, command='add_attachment_to_task')

    await state.update_data(task_id=task_id)
    await state.set_state(AddingAttachmentStates.waiting_for_attachment)
    await message.answer('Choose attachment')

    logger.info('Asked for attachment', task_id=task_id, command='add_attachment_to_task')

    # TODO: check that only one attachment is sent


@task_router.message(AddingAttachmentStates.waiting_for_attachment)
async def add_attachment__attachment_chosen(message: Message, state: FSMContext) -> None:
    task_id = await state.get_value('task_id')
    logger.info('attachment chosen', task_id=task_id, command='add_attachment_to_task')

    file = await _get_tg_file(message)
    tg_file_url = f"https://api.telegram.org/file/bot{message.bot.token}/{file.file_path}"
    async with aiohttp.request('get', tg_file_url) as tg_file_response:
        async with httpx.AsyncClient(timeout=httpx.Timeout(200)) as client:
            upload_response = await client.post(
                str(Url(endpoint=f'tasks/tasks/{task_id}/attachments/')),
                content=AsyncIterableOverStreamReader(tg_file_response.content),
                headers={
                    # NOTE (SemenK): as of 2025-07-04 telegram doesn't keep filename for images.
                    # so if filename is None, it means it's an image => .jpg
                    'Filename': _get_tg_file_name(message) or 'autogenerated_filename.jpg',
                    "Content-Length": str(file.file_size),
                }
            )

            if upload_response.status_code == 201:
                logger.info(
                    'attachment uploaded',
                    attachment_url=upload_response.json()['attachment_url'], task_id=task_id,
                    command='add_attachment_to_task',
                )
                await message.answer(upload_response.json()['attachment_url'])
            else:
                logger.info(
                    'something went wrong during attachment upload',
                    attachment_url=(upload_response.json()), task_id=task_id, command='add_attachment_to_task',
                )
                await message.answer(upload_response.text)

            await state.clear()


async def _get_tg_file(message: Message) -> File:
    if message.document:
        file_id = message.document.file_id
    elif message.animation:
        file_id = message.animation.file_id
    elif message.audio:
        file_id = message.audio.file_id
    elif message.video:
        file_id = message.video.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id
    else:
        raise ValueError('File must be either document or animation or audio or video or photo')
    file = await message.bot.get_file(file_id)
    return file


def _get_tg_file_name(message: Message) -> str | None:
    if message.document or message.animation:
        return message.document.file_name
    elif message.animation:
        return message.animation.file_name
    elif message.audio:
        return message.audio.file_name
    elif message.video:
        return message.video.file_name
    elif message.photo:
        return None
    else:
        raise ValueError('File must be either document or animation or audio or video or photo')


class AsyncIterableOverStreamReader:
    CHUNK_SIZE = 5 * 1024 * 1024

    def __init__(self, stream_reader: StreamReader) -> None:
        self._stream_reader = stream_reader

    async def __aiter__(self) -> AsyncGenerator:
        while chunk := await self._stream_reader.read(self.CHUNK_SIZE):
            yield chunk
