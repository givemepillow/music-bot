from aiogram.types import CallbackQuery

from app.core.loader import dp


@dp.callback_query_handler(text=['_'], state='*')
async def plug(callback_query: CallbackQuery):
    """
    Хендлер-заглушка для моментального ответа на пустую кнопку в инлайн-меню.
    :param callback_query: Callback Query
    """
    await callback_query.answer()
