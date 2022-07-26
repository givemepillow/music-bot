import sys
import warnings

import loguru

from app.core.loader import bot_engine
from app.core.loader import dp
from app.core.handlers.registry import setup_handlers

warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
loguru.logger.remove()
loguru.logger.add(
    sink=sys.stdout,
    format="{level} {time:MMM DD HH:mm:ss.SSS}: {message}",
    enqueue=True
)

if __name__ == '__main__':
    setup_handlers(dp)
    loguru.logger.info(
        f"Number of message handlers: {len(dp.message_handlers.handlers)}."
    )
    loguru.logger.info(
        f"Number of callback query handlers: {len(dp.callback_query_handlers.handlers)}."
    )
    bot_engine.start()
