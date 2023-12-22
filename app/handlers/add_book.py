from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import db
from states import AddBook
from keyboards import submit_or_cancel_keyboard, cancel_keyboard
from utils.manage_state import delete_message_and_update_state

router = Router()


@router.callback_query(F.data == "book_add")
async def enter_book_title(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите название книги:", reply_markup=cancel_keyboard)

    payload = {"last_message": call.message.message_id}
    await delete_message_and_update_state(state=state, new_state=AddBook.book_title, new_data=payload)


@router.message(F.text, AddBook.book_title)
async def enter_book_description(message: Message, state: FSMContext):
    message_new = await message.answer("Введите описание", reply_markup=cancel_keyboard)

    payload = {"last_message": message_new.message_id, "book_title": message.text}
    await delete_message_and_update_state(state=state, new_state=AddBook.book_description, new_data=payload,
                                          chat_id=message.chat.id)


@router.message(F.text, AddBook.book_description)
async def enter_book_genre(message: Message, state: FSMContext):
    list_genres = await db.select_genres()

    builder = InlineKeyboardBuilder()

    for genre in list_genres:
        builder.add(InlineKeyboardButton(text=f"{genre[1]}", callback_data=f"genre_{genre[0]}"))

    builder.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
    builder.adjust(2)  # максимум 2 столбика в строчке

    message_new = await message.answer("Введите или выберите жанр",
                                       reply_markup=builder.as_markup(resize_keyboard=True))

    payload = {"last_message": message_new.message_id, "book_description": message.text}
    await delete_message_and_update_state(state=state, new_state=AddBook.book_genre, new_data=payload,
                                          chat_id=message.chat.id)


@router.callback_query(AddBook.book_genre, F.data.startswith("genre_"))
async def enter_book_author(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите автора", reply_markup=cancel_keyboard)

    payload = {"last_message": call.message.message_id, "book_genre_id": int(call.data[6:])}  # genre_123 -> 123
    await delete_message_and_update_state(state=state, new_state=AddBook.book_author, new_data=payload)


@router.message(F.text, AddBook.book_genre)
async def enter_book_description(message: Message, state: FSMContext):
    message_new = await message.answer("Введите автора", reply_markup=cancel_keyboard)

    payload = {"last_message": message_new.message_id, "book_genre_id": None, "book_genre_name": message.text}
    await delete_message_and_update_state(state=state, new_state=AddBook.book_author, new_data=payload,
                                          chat_id=message.chat.id)


@router.message(F.text, AddBook.book_author)
async def enter_book_submit(message: Message, state: FSMContext):
    data = await state.get_data()

    if data['book_genre_id']:
        genre_info = (await db.select_genre(data['book_genre_id']))[1]
    else:
        genre_info = data["book_genre_name"]

    text = f"""
Подтвердите добавление книги

Название: {data['book_title']}
Описание: {data['book_description']}
Жанр: {genre_info}
Автор: {message.text}
    """

    message_new = await message.answer(text, reply_markup=submit_or_cancel_keyboard)

    payload = {"last_message": message_new.message_id, "book_author": message.text}
    await delete_message_and_update_state(state=state, new_state=AddBook.submit, new_data=payload,
                                          chat_id=message.chat.id)


@router.callback_query(F.data == "submit", AddBook.submit)
async def enter_book_description(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if data['book_genre_id']:
        # если пользователь выбрал предоставленный жанр
        genre_info = data["book_genre_id"]
    else:
        # если пользователь передал жанр текстом
        genre_info = await db.add_genre(data["book_genre_name"])

    await db.add_new_book(
        user_id=call.from_user.id,
        title=data["book_title"],
        description=data["book_description"],
        genre_id=genre_info,
        author=data['book_author']
    )

    # подтверждаем добавление книги пользовалю, удаляем inline-клавиатуру
    await call.message.edit_text(call.message.text + "\n\nКнига добавлена", reply_markup=None)

    # удаляем нужные данные из состояния
    for _ in ["book_title", "book_description", "book_genre_id", "book_author", 'book_genre_name']:
        try:
            data.pop(_)
        except (Exception,):
            pass

    await state.set_data(data)
