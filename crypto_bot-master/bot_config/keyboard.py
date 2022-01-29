# Библиотеки
from aiogram import types
from aiogram.dispatcher.filters import Text
from pars import bot_parser as parser
import asyncio
import bot_config.data



def Buttoms(dp,bot,chat_id,access_id):

    def Treatment(btc):  # Обработка вывода
        str1=""
        for i in range(len(btc)):
            if (btc[i][3][0]<1):  # Убираем лишние нули и преобразуем формат 5e-5 в формат 0.00005
                commission_in_usd = str(("{:f}".format(float(btc[i][3][0])))).rstrip("0").rstrip(".")
            else:
                commission_in_usd=str(btc[i][3][0]).rstrip("0").rstrip(".")

            if (btc[i][0]<1 and btc[i][0]!=False):  # Убираем лишние нули и преобразуем формат 5e-5 в формат 0.00005
                price_in_usd = str(("{:f}".format(float(btc[i][0])))).rstrip("0").rstrip(".")
            elif (btc[i][0]==False):
                price_in_usd="Недоступна"
            else:
                price_in_usd=str(btc[i][0]).rstrip("0").rstrip(".")
                price_in_usd+="$"
            status = "Закрыта" if btc[i][2]==0 else "Открыта"
            dep = "Есть" if btc[i][4]==1 else "Нету"
            str1=str1 + f"\n {i+1}) Стоимость в долларах: <b>{price_in_usd}</b>; Сеть: <b>{btc[i][1]}</b>; Статус: <b>{status}</b>; " \
                        f"Коммисия в валюте: <b> {commission_in_usd}</b>; Коммисия в долларах: <b>{btc[i][3][1]}$</b>; " \
                        f"Возможность депозита: <b>{dep}</b>. \n"
        return(str1)


    async def mail(wait_for,access_id):
        while True:
            await asyncio.sleep(wait_for)
            a=parser.Output()
            output1 = a.network_change()
            output2 = a.appear_or_disappear()
            output3 = a.deposit_change()
            bot_config.data.sd = parser.Output().data
            if output1 != False:
                for j in range(len(output1)):
                    message = f"Для монеты  <b>{output1[j][1][0]}</b>"
                    if output1[j][0] == 2:
                        message += ' cтатус сети(ей) <b>вывода изменился:</b> \n\n'
                        for k in range(len(output1[j][1][1][1])):
                            if output1[j][1][1][1][k][2] == 1:
                                message += f"{k + 1}) Cеть <b>{output1[j][1][1][1][k][1]} открылась</b> \n"
                            else:
                                message += f"{k + 1}) Cеть: <b>{output1[j][1][1][1][k][1]} закрылась</b> \n"
                            if output1[j][1][1][1][k][0] == 0:
                                message += f"Цена в долларах <b>недоступна</b>\n"
                            else:
                                message += f"Цена монеты в долларах: <b>{output1[j][1][1][1][k][0]} $</b> \n"
                            message += f"Комиссия составляет <b>{output1[j][1][1][1][k][3][1]} $</b> или <b>{output1[j][1][1][0][k][3][0]}</b> самой валюты \n\n"
                    for i in access_id:
                        await bot.send_message(chat_id=i,
                                               text=message)  # чтобы отправлять сообщения нескольким пользователям сразу
            if output2[0] != False:
                message = f""
                for j in range(len(output2[1][0])):
                    message = f"Монета <b>{output2[1][0][j]} исчезла</b>\n"
                for j in range(len(output2[1][1])):
                    message += f"Монета <b>{output2[1][1][j]} появилась</b>\n"
                for i in access_id:
                    await bot.send_message(chat_id=i,
                                           text=message)  # чтобы отправлять сообщения нескольким пользователям сразу
            if output3 != False:
                for j in range(len(output3)):
                    message = f"Для монеты <b>{output3[j][1][0]}</b> статус сети(ей) <b>ввода изменился</b>\n\n"
                    for k in range(len(output3[j][1][1][1])):
                        if output3[j][1][1][1][k][4] == 1:
                            message += f"{k + 1}) Cеть <b>{output3[j][1][1][1][k][1]} открылась для ввода</b> \n"
                        else:
                            message += f"{k + 1}) Cеть: <b>{output3[j][1][1][1][k][1]} закрылась для ввода</b> \n"
                        if output3[j][1][1][1][k][0] == 0:
                            message += f"Цена в долларах <b>недоступна</b> \n\n"
                        else:
                            message += f"Цена монеты в долларах: <b>{output3[j][1][1][1][k][0]} $</b> \n\n"
                    for i in access_id:
                        await bot.send_message(chat_id=i,
                                               text=message)  # чтобы отправлять сообщения нескольким пользователям сразу

    loop = asyncio.get_event_loop()  # Получение цикла событий, которые должны выполняться асинхронно
    loop.create_task(mail(55, access_id)) # Вызываем функцию рассылки

    @dp.message_handler(commands="start")
    async def tap1(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ("Bitcoin", "Ethereum", "Другая")
        keyboard.add(*buttons)
        if message.from_user.id in chat_id:
            if message.from_user.id not in access_id:
                access_id.append(message.from_user.id)
            await message.answer("Рассылка включена")
            await message.answer("Выберите криптовалюту", reply_markup=keyboard)

        else:
            await message.answer("Нет доступа")


    @dp.message_handler(commands="continue")
    async def tap2(message: types.Message):
        # добавление в цикл событий функцию рассылки
        if message.from_user.id in chat_id:
            if message.from_user.id not in access_id:
                access_id.append(message.from_user.id)
            await message.answer("Рассылка включена")


    @dp.message_handler(commands="stop")
    async def tap3(message: types.Message):
        if message.from_user.id in chat_id:
            if message.from_user.id in access_id:
                access_id.remove(message.from_user.id)
            await message.answer("Рассылка остановлена")


    @dp.message_handler(Text(equals="Bitcoin"))
    async def variant1(message: types.Message):
        if message.from_user.id in chat_id:
            str1=Treatment(parser.Output().data["BTC"])
            await message.reply(str1)


    @dp.message_handler(Text(equals="Ethereum"))
    async def variant2(message: types.Message):
        if message.from_user.id in chat_id:
            str1 = Treatment(parser.Output().data["ETH"])
            await message.reply(str1)


    @dp.message_handler(Text(equals="Другая"))
    async def variant3(message: types.Message):
        if message.from_user.id in chat_id:
            await message.answer("Введите тикер криптовалюты (например: <b>BTC</b> для Bitcoin)")


    @dp.message_handler(lambda message: message.text)
    async def variant4(message: types.Message):
        if message.from_user.id in chat_id:
            str1 = Treatment(parser.Output().data[(message.text).upper()])
            await message.reply(str1)


    # Регитсрация кнопок
    dp.register_message_handler(tap1, commands="start")
    dp.register_message_handler(tap2, commands="continue")
    dp.register_message_handler(tap3, commands="stop")

