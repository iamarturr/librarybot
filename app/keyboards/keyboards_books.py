from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Отмена", callback_data="cancel")]
])

submit_or_cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Отмена", callback_data="cancel")],
    [InlineKeyboardButton(
        text="Подтвердить", callback_data="submit")]
])

# ...page_0 - первая страница в пагинации
start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Все книги", callback_data="books_page_0")],
    [InlineKeyboardButton(
        text="Мои Книги", callback_data="my_books_page_0")],
    [InlineKeyboardButton(
        text="Добавить книги", callback_data="book_add")]
])
