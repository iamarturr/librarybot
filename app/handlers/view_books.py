from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from app import db

router = Router()


@router.callback_query(F.data.startswith("my_books_page_"))
@router.callback_query(F.data.startswith("books_page_"))
async def all_books_pagination(call: CallbackQuery, state: FSMContext, limit: int = 10):
    if call.data.startswith("books_page_"):
        user_id = None  # не учитываем user_id, а выбираем все книги
        payload = "books_page_"  # books_p... - все книги в бд
        offset = int(call.data[11:])  # books_page_123 -> 123

        # при нажатии назад в фильтрах возвращал
        # пользователя в список всех книг, а не в главное меню
        payload_filter = "filters_books_page_0"
    elif call.data.startswith("my_books_page_"):
        user_id = call.from_user.id  # учитываем user_id, выбираем книги пользователя
        payload = "my_books_page_"  # my_books... - книги текущего пользователя
        offset = int(call.data[14:])  # my_books_page_123 -> 123

        # при нажатии назад в фильтрах возвращал
        # пользователя в список его книг, а не в главное меню
        payload_filter = "filters_my_books_page_0"
    else:
        return await call.answer("Неизвестный payload!", show_alert=True)

    data = await state.get_data()

    # search_text / genre_id = None, пользователь не ввел текста / жанра для поиска
    search_text = None
    if 'search_text' in data:
        search_text = data['search_text']

    genre_id = None
    if 'genre_id' in data:
        genre_id = data['genre_id']

    # offset - смещение для создания пагинации
    # limit - макс. кол-во возвращаемых строк на одной странице (default 10)
    # search_text - текст для поиска в имени автора/названии книги
    # genre_id - id жанра в таблице genres
    # если search_text/genre_id = None, то аргумент не учитывается
    result, prev_page, next_page = await db.select_books(user_id=user_id, offset=offset, limit=limit,
                                                         search_text=search_text, genre_id=genre_id)

    # собираем все N (default 10) книг в один столбик
    # а кнопки для пагинации в три столбика
    list_keyboard = []
    for book in result:
        list_keyboard.append(
            [InlineKeyboardButton(text=f"[{book[0]}] {book[1]} ({book[2]})", callback_data=f"watch_book_{book[0]}")])

    bottom_keyboard = []

    if prev_page:
        bottom_keyboard.append(InlineKeyboardButton(text="←", callback_data=f"{payload}{offset - 10}"))

    bottom_keyboard.append(InlineKeyboardButton(text="Фильтры", callback_data=payload_filter))

    if next_page:
        bottom_keyboard.append(InlineKeyboardButton(text="→", callback_data=f"{payload}{offset + 10}"))

    list_keyboard.append(bottom_keyboard)
    list_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="menu")])

    markup = InlineKeyboardMarkup(inline_keyboard=list_keyboard)

    await call.message.edit_text("Список книг:", reply_markup=markup)
