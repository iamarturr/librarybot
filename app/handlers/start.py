from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.keyboards_books import start_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Меню:", reply_markup=start_keyboard)


@router.callback_query(F.data == "menu")
async def start_call(call: CallbackQuery):
    await call.message.edit_text("Меню:", reply_markup=start_keyboard)


@router.callback_query(F.data == "cancel")
async def cancel(call: CallbackQuery, state: FSMContext):
    has_state = await state.get_state()
    await call.message.delete()

    if has_state is not None:
        data = await state.get_data()

        # удаляем нужные данные из состояния
        for _ in ["book_title", "book_description", "book_genre_id", "book_author", 'book_genre_name']:
            try:
                data.pop(_)
            except (Exception,):
                pass

        await state.set_data(data)
        await call.answer("Действие отменено!", show_alert=True)
        await start(call.message)
