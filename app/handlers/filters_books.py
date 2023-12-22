from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import db
from keyboards import cancel_keyboard
from states.states_books import FiltersSearch
from utils.manage_state import delete_message_and_update_state

router = Router()


@router.callback_query(F.data.startswith("filters_"))
async def set_filters(call: CallbackQuery, state: FSMContext):
    # filters_books_page_0 -> books_page_0 // filters_my_books_page_0 -> my_books_page_0
    # при нажатии на кнопку назад, возвращает пользователя, откуда он перешел в фильтры (все/свои книги)

    back_data = call.data[8:]
    data = await state.get_data()

    if call.data.startswith("filters_"):
        await state.update_data({"back": back_data})
    else:
        back_data = data["back"]

    keyboard = []

    text = f"""
Фильтры:

Текст: {data['search_text'] if 'search_text' in data else '-'}
Жанр: {data['genre_name'] if 'genre_name' in data else '-'}
    """

    if "search_text" in data:
        keyboard.append([InlineKeyboardButton(text="Сбросить текст поиска", callback_data="clear_search_text")])
    else:
        keyboard.append([InlineKeyboardButton(text="Ввести текст для поиска", callback_data="set_search_text")])

    keyboard.append([InlineKeyboardButton(text="Выбрать жанр", callback_data="set_genre")])
    keyboard.append([InlineKeyboardButton(text="Назад", callback_data=back_data)])

    buttons = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await call.message.edit_text(text, reply_markup=buttons)


@router.callback_query(F.data == "set_search_text")
async def set_text_for_search(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите текст для поиска:", reply_markup=cancel_keyboard)

    payload = {"last_message": call}
    await delete_message_and_update_state(state=state, new_state=FiltersSearch.set_search, new_data=payload)


@router.message(F.text, FiltersSearch.set_search)
async def enter_book_author(message: Message, state: FSMContext):
    data = await state.get_data()

    await state.update_data({'search_text': message.text})

    await message.delete()
    await state.set_state()

    await set_filters(data['last_message'], state)


@router.callback_query(F.data == "clear_search_text")
async def clear_filters(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # удаляем поисковой текст
    if "search_text" in data:
        data.pop("search_text")

    await state.set_data(data)  # обновляем состояние
    await set_filters(call, state)


@router.callback_query(F.data == "set_genre")
async def clear_search_text(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    genres = await db.select_genres()

    builder = InlineKeyboardBuilder()

    for genre in genres:
        builder.add(InlineKeyboardButton(text=f"{genre[1]}", callback_data=f"search_genre_{genre[0]}"))

    if "genre_id" in data or "genre_name" in data:
        builder.add(InlineKeyboardButton(text="Сбросить жанр", callback_data="clear_genre"))

    builder.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    builder.adjust(2)  # максимум 2 столбика в строчке

    await call.message.edit_text("Введите текст для поиска:", reply_markup=builder.as_markup())


@router.callback_query(F.data == "clear_genre")
async def clear_filters(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    # удаляем id жанра
    if "genre_id" in data:
        data.pop("genre_id")

    # удаляем название жанра
    if "genre_name" in data:
        data.pop("genre_name")

    await state.set_data(data)  # обновляем состояние
    await set_filters(call, state)


@router.callback_query(F.data.startswith("search_genre_"))
async def search_genre(call: CallbackQuery, state: FSMContext):
    genre_id = call.data[13:]  # search_genre_123 -> 123
    genre_info = await db.select_genre(int(genre_id))

    if not genre_info:
        return await call.answer("Данный жанр не найден!", show_alert=True)

    await state.update_data({"genre_id": int(genre_id), "genre_name": genre_info[1]})
    await set_filters(call, state)
