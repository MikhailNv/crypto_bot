# Библиотеки
import logging
import bot_config.data as data
from aiogram import Bot, Dispatcher, types, executor
import asyncio
from pars import bot_parser as parser
import bot_config.keyboard

# Работа клавиатуры
chat_id = data.id_a
access_id =data.id_a
# Объект бота
bot = Bot(data.token, parse_mode=types.ParseMode.HTML)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

bot_config.keyboard.Buttoms(dp, bot, chat_id, access_id)

if __name__ == '__main__':
    bot_config.data.sd=parser.Output().data
    executor.start_polling(dp, skip_updates=True)
