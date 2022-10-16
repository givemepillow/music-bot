from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from app.core.extensions import MessageBox
from app.core.loader import bot


class InlineStack(MessageBox):
    @classmethod
    async def delete_all(cls, user_id: int):
        try:
            while _message := cls.get(user_id=user_id):
                if user_id in cls._messages:
                    cls._messages[user_id].discard(_message.message_id)
                await bot.delete_message(chat_id=user_id, message_id=_message.message_id)
        except (MessageCantBeDeleted, MessageToDeleteNotFound):
            cls._messages[user_id].clear()
