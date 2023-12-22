from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State

from app import bot


async def delete_message_and_update_state(state: FSMContext, new_state: State, new_data: dict = None,
                                          chat_id: int = None):
    data = await state.get_data()

    # если есть сообщения для удаления в состоянии
    if "last_message" in data and data["last_message"] is not None and chat_id is not None:
        await bot.delete_message(chat_id, data["last_message"])

    # обновляем состояние и добавляем новые данные
    await state.set_state(new_state)
    await state.set_data({**data, **new_data})
