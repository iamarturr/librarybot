from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from data import config
from utils import Database

db = Database("database.db")
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(config.BOT_TOKEN)