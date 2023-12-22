from aiogram.fsm.state import StatesGroup, State


class AddBook(StatesGroup):
    book_title = State()
    book_author = State()
    book_genre = State()
    book_description = State()
    submit = State()


class FiltersSearch(StatesGroup):
    set_search = State()