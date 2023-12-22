from typing import Optional

from aiosqlite import connect, Connection, Cursor
from logging import getLogger

import datetime


def _get_unix():
    return int(datetime.datetime.utcnow().timestamp())


class Database:
    def __init__(self, filename: str):
        self.filename = filename
        self.connection: Optional[Connection] = None
        self.cursor: Optional[Cursor] = None
        self.logger = getLogger(__name__)

    async def create_connection(self):
        self.connection = await connect(self.filename)
        self.cursor = await self.connection.cursor()

        self.logger.info(f'Connected to a {self.filename} database.')

    async def fetch_all(self, sql: str, params: tuple = ()):
        await self.cursor.execute(sql, params)
        return await self.cursor.fetchall()

    async def fetch_one(self, sql: str, params: tuple = ()):
        await self.cursor.execute(sql, params)
        return await self.cursor.fetchone()

    async def commit(self, sql: str, values: tuple = ()):
        await self.cursor.execute(sql, values)
        await self.connection.commit()

    async def create_tables(self):
        await self.commit(f"""
            CREATE TABLE IF NOT EXISTS genres (
                genre_id INTEGER PRIMARY KEY,
                genre_name VARCHAR(50) NOT NULL UNIQUE
            );
        """)

        await self.commit("""
            INSERT INTO genres (genre_name)
            VALUES
               ('видения'), ('новелла'), ('ода'), ('опус'),
               ('очерк'), ('поэма'), ('повесть'), ('пьеса')
            ON CONFLICT (genre_name) DO NOTHING;
        """)

        await self.commit(f"""
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(31),
                description TEXT,
                genre_id INT,
                user_added INT,
                created INT,
                FOREIGN KEY (genre_id) REFERENCES genres (genre_id)
            );
        """)

        self.logger.info(f'Connected to a {self.filename} database.')

    async def select_books(self, user_id: int = None, offset: int = 0, search_text: str = None, genre_id: int = None,
                           limit: int = 10):
        # собираем все запросы в один список
        # а также все данные к этим запросам в другой список

        where_conditions = []
        params = []

        if user_id:
            where_conditions.append("user_added = ?")
            params.append(user_id)

        if search_text:
            where_conditions.append("(author LIKE ? OR title LIKE ?)")
            params.extend([f"%{search_text}%", f"%{search_text}%"])

        if genre_id:
            where_conditions.append("genre_id = ?")
            params.append(genre_id)

        where_query = " AND ".join(where_conditions) if where_conditions else ""

        if where_query:
            where_query = "WHERE " + where_query

        query = f"""
            SELECT book_id, title, author
            FROM books
            {where_query}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        result = await self.fetch_all(query, tuple(params))

        if offset >= 10:
            # проверяем есть ли предыдущая страница
            previous_page_exists = bool(await self.fetch_one(f"""
                SELECT 1
                FROM books
                {where_query}
                LIMIT ? OFFSET ?
            """, tuple(params[:-1]) + (offset - limit,)))
        else:
            previous_page_exists = None

        # проверяем есть ли след страница
        next_page_exists = bool(await self.fetch_one(f"""
            SELECT 1
            FROM books
            {where_query}
            LIMIT ? OFFSET ?
        """, tuple(params[:-1]) + (offset + limit,)))

        return result, previous_page_exists, next_page_exists

    async def add_new_book(self, user_id: int, title: str, description: str, genre_id: int, author: str):
        unix = _get_unix()

        query = """
            INSERT INTO books (title, author, description, genre_id, user_added, created)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        values = (title, author, description, genre_id, user_id, unix)

        await self.commit(query, values)

    async def select_genres(self):
        return await self.fetch_all(f"SELECT * FROM genres")

    async def select_genre(self, genre_id: int):
        return await self.fetch_one("SELECT * FROM genres WHERE genre_id = ?", (genre_id,))

    async def select_book(self, book_id: int):
        query = """
            SELECT books.*, genres.genre_name
            FROM books 
            LEFT JOIN genres ON books.genre_id = genres.genre_id
            WHERE book_id = ?
        """
        return await self.fetch_one(query, (book_id,))

    async def delete_book(self, book_id: int):
        await self.commit("DELETE FROM books WHERE book_id = ?", (book_id,))

    async def add_genre(self, name: str) -> int:
        genre = await self.fetch_one("SELECT * FROM genres WHERE genre_name = ?", (name.strip(),))
        if genre:
            return genre[0]
        else:
            query = """INSERT INTO genres (genre_name) VALUES (?)"""
            values = (name,)

            await self.commit(query, values)
            return (await self.fetch_one("SELECT * FROM genres WHERE genre_name = ?", (name.strip(),)))[0]
