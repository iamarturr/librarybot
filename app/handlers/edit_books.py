from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app import db
from handlers.start import start

router = Router()


@router.callback_query(F.data.startswith("watch_book_"))
async def book_card(call: CallbackQuery):
    book_id = call.data[11:]  # book_1 -> 1
    book = await db.select_book(int(book_id))

    if not book:
        return await call.answer("Данная книга не найдена!", show_alert=True)

    text = f"""
Информация о книге

ID: {book[0]}
Название: {book[1]}
Описание: {book[3]}
Жанр: {book[7]}
Автор: {book[2]}
    """

    builder = InlineKeyboardBuilder()

    # book[5] - user_id
    if call.from_user.id == book[5]:
        builder.add(InlineKeyboardButton(text=f"Удалить книгу", callback_data=f"delete_book_{book[0]}"))

    builder.add(InlineKeyboardButton(text="Назад", callback_data="menu"))
    builder.adjust(1)  # все кнопки в один столбик

    await call.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("delete_book_"))
async def delete_book(call: CallbackQuery):
    book_id = int(call.data[12:])  # delete_book_123 -> 123
    book = await db.select_book(int(book_id))

    if not book:
        return await call.answer("Данная книга не найдена!", show_alert=True)

    # book[5] - user_id
    if call.from_user.id != book[5]:
        return await call.answer("Вы не можете удалить данную книгу!", show_alert=True)

    await db.delete_book(book_id)

    await call.answer("Книга удалена!", show_alert=True)
    await call.message.delete()
    await start(call.message)
