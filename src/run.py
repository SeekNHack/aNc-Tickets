import logging
from aiogram import types

from aiogram.utils import executor

from .settings import dispatcher
from .database import database

def run() -> None:
    allowed_updates = types.AllowedUpdates.MESSAGE | types.AllowedUpdates.CALLBACK_QUERY
    logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(dispatcher.dp, skip_updates=True, allowed_updates=allowed_updates)