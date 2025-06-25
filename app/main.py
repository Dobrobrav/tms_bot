import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from start_handlers import start_router

load_dotenv(dotenv_path=(Path(__file__).resolve().parent.parent / '.env'))

from user_handlers import user_router
from task_handlers import task_router
from comment_handlers import comment_router

from aiogram import Bot, Dispatcher

import structlog
import sys
from datetime import datetime

# ANSI escape-коды
RESET = "\033[0m"
COLORS = {
    "critical": "\033[1;31m",
    "error": "\033[31m",
    "warning": "\033[33m",
    "info": "\033[32m",
    "debug": "\033[36m",
}
KEY_COLOR = "\033[36m"
VAL_COLOR = "\033[35m"
TIME_COLOR = "\033[90m"  # тёмно-серый


def custom_renderer(_, __, event_dict):
    level = event_dict.pop("level", "info").lower()
    ts = datetime.now().isoformat(timespec="seconds")

    color = COLORS.get(level, "")
    parts = [
        f"{TIME_COLOR}{ts}{RESET}",
        f"{color}[{level:<8}]{RESET}",
    ]

    for key, value in event_dict.items():
        parts.append(f"{KEY_COLOR}{key}{RESET}={VAL_COLOR}{value}{RESET}")

    return " ".join(parts)


structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        custom_renderer,
    ],
    logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
)

log = structlog.get_logger()

logger = structlog.get_logger(__name__)

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

API_TOKEN = os.environ['API_TOKEN']


async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(start_router, user_router, task_router, comment_router)
    bot = Bot(API_TOKEN)
    logger.info('bot (probably) started')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
