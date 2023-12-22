import asyncio
import logging

from app import dp, bot, db

from handlers import (
    add_book, edit_books, filters_books, view_books,
    start
)


async def create_db():
    await db.create_connection()
    await db.create_tables()


async def main():
    dp.include_routers(
        add_book.router, filters_books.router, view_books.router,
        edit_books.router, start.router
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    await create_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, db=db)


if __name__ == '__main__':
    asyncio.run(main())
