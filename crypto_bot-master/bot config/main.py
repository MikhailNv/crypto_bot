import logging, data
from aiogram import Bot, Dispatcher, executor, types

# Объект бота
bot = Bot(data.token)
# Диспетчер для бота
dp = Dispatcher(bot)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)


# Хэндлер на команду /test1
@dp.message_handler(commands="start")
async def tap1(message: types.Message):
    await message.answer("Hi")

# Хэндлер на команду /test2
@dp.message_handler(commands="help")
async def tap2(message: types.Message):
    await message.bot.send_dice(645454958, emoji="🎰")

# Где-то в другом месте...
dp.register_message_handler(tap1, commands="start")
dp.register_message_handler(tap2, commands="help")


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)