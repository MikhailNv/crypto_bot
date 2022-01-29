import hashlib
import hmac
import json
import time
import calendar
import requests
import bot_config.data
import pars.config


class Loginer():
    # Создание запроса к серверу о его upTime
    def __init__(self):
        try:
            self.servertime = requests.get("https://api.binance.com/api/v3/time")
        except requests.exceptions.ConnectionError:
            while True:
                self.servertime = requests.get("https://api.binance.com/api/v3/time")
                if self.servertime.ok == True:
                    break
        self.servertimeobj = json.loads(self.servertime.text)
        self.servertimeobj = self.servertimeobj['serverTime']

    # Запрос авторизации на сервере и получение информции обо всех валютах
    def login(self):
        queryString = 'timestamp='+str(self.servertimeobj)
        signature = hmac.new(pars.config.apiSecret.encode('utf-8'), queryString.encode('utf-8'), hashlib.sha256).hexdigest()
        session = requests.get('https://api.binance.com/sapi/v1/capital/config/getall',
                               params={
                                "timestamp": str(self.servertimeobj),
                                "signature": signature,
                            },
                               headers={'X-MBX-APIKEY': pars.config.apiKey})
        return json.loads(session.text)

class Parser(Loginer):
    # Подключаем конструктор из родительского класса и сохраняем ответ сервера
    def __init__(self):
        Loginer.__init__(self)
        self.info_about_coins = self.login()
        #print(self.info_about_coins)

    # Создаем парсер необходимых для нас данных
    def parsers(self):
        dict_of_coins = {}
        price = requests.get('https://api.binance.com/api/v3/ticker/price')
        price_dict = json.loads(price.text)
        # price_dict_list = [[price_dict[key]['symbol'][:-4], price_dict[key]['price']] for key in range(len(price_dict))
        #                    if 'USDT' in price_dict[key]['symbol']]
        price_dict_list = [[price_dict[key]['symbol'][:-4] if len(price_dict[key]['symbol']) - 4 == price_dict[key]['symbol'].find("USDT") else None, price_dict[key]['price']] for key in range(len(price_dict))
                           if 'USDT' in price_dict[key]['symbol']]
        #print(price_dict_list)
        for dict in range(len(self.info_about_coins)):
            coin = self.info_about_coins[dict]['coin']
            dict_of_coins.setdefault(coin, [])
            for net in range(len(self.info_about_coins[dict]['networkList'])):
                network = self.info_about_coins[dict]['networkList'][net]['network']
                withdrawEnable = self.info_about_coins[dict]['networkList'][net]['withdrawEnable']
                depositEnable = self.info_about_coins[dict]['networkList'][net]['depositEnable']
                self.withdrawFee = self.info_about_coins[dict]['networkList'][net]['withdrawFee']
                count = 0
                for coins in price_dict_list:
                    if coins[0] == coin:
                        dict_of_coins[coin].append((float(coins[1]),
                                                    network,
                                                    1 if withdrawEnable == True else 0,
                                                    (float((self.withdrawFee)),
                                                     round(float(self.withdrawFee)*float(coins[1]), 2)),
                                                    1 if depositEnable == True else 0))
                        count = 1
                        """
                           dict_of_coins - словарь, ключами которого являются названия валют, а их значениями - списки
                           со вложенными кортежами(в зависимости от кол-ва сетей вывода)
                           HINT! О некоторых валютах Binance не предоставляет информацию по выводу в USDT.
                           Позиция в кортеже / ее наименование:
                           1) (0) - Цена валюты в долларах(если значение цены = 0, значит она неконвертируема в USDT)
                           2) (1) - Сеть
                           3) (2) - Статус, где 1 - Открыта, 0 - Закрыта
                           4) (3) - Комиссия, состоит из кортежа, где первый элемент - комиссия в самой валюте,
                                                                      второй элемент - комиссия в долларах
                           5) (4) - Возможность депозита, где 1 - положительна(True), 0 - отрицательна(False)
                        """
                    else:
                        continue
                # Добавление неконвертируемой валюты
                if count == 0:
                    dict_of_coins[coin].append((False, network, 1 if withdrawEnable == True else 0,
                                                (float(self.withdrawFee), 0.0), 1 if depositEnable == True else 0))
        return dict_of_coins


class Output(Parser):
    def __init__(self):
        Parser.__init__(self)
        self.data = self.parsers()
        self.saved_data = bot_config.data.sd

    def keys(self, data_to_keys):
        key_list = []
        list_of_keys = data_to_keys.keys()
        for k in list_of_keys:
            key_list.append(k)
        return key_list

    def old_and_new(self):
        old_data = self.saved_data
        new_data = self.data
        old_keys = self.keys(old_data)
        new_keys = self.keys(new_data)
        return [old_data, new_data, sorted(old_keys), sorted(new_keys)]

    def appear_or_disappear(self):
        data_keys = self.old_and_new()
        old_keys = data_keys[2]
        new_keys = data_keys[3]
        app_list = []
        dis_list = []
        key_list = []
        if old_keys == new_keys:
            return [False, (False, False), sorted(old_keys)]
        else:
            old_set = set()
            new_set = set()
            old_set.update(old_keys)
            new_set.update(new_keys)
            dif_old = old_set - new_set
            dif_new = new_set - old_set
            for k in dif_old:
                dis_list.append(k)
            for k in dif_new:
                app_list.append(k)
            set.intersection_update(old_set, new_set)
            for k in old_set:
                key_list.append(k)
            flag = str(len(dis_list)) + str(len(app_list))
            return [flag, (sorted(dis_list), sorted(app_list)), sorted(key_list)]

    def network_change(self):
        old_and_new = self.old_and_new()
        old_one = old_and_new[0]
        new_one = old_and_new[1]
        outlist = []
        app_or_dis = self.appear_or_disappear()
        flag = 0
        key_list = app_or_dis[2]
        for i in range(len(key_list)):
            ok = old_one[key_list[i]]
            nk = new_one[key_list[i]]
            if len(ok) != len(nk):
                if len(ok) > len(nk):
                    flag = 11
                if len(nk) > len(ok):
                    flag = 12
                outlist.append([flag, [key_list[i], (ok, nk)]])
            else:
                for j in range(len(old_one[key_list[i]])):
                    cur_net_old = ok[j]
                    cur_net_new = nk[j]
                    if not (cur_net_new[1] == cur_net_old[1] and cur_net_new[2] == cur_net_old[2]):
                        flag = 2
                        outlist.append([flag, [key_list[i], (ok, nk)]])
        if flag == 0:
            return False
        else:
            return outlist

    def deposit_change_first(self):
        old_and_new = self.old_and_new()
        old_one = old_and_new[0]
        new_one = old_and_new[1]
        outlist = []
        app_or_dis = self.appear_or_disappear()
        flag = 0
        key_list = app_or_dis[2]
        for i in range(len(key_list)):
            ok = old_one[key_list[i]]
            nk = new_one[key_list[i]]
            if len(ok) == len(nk):
                for j in range(len(old_one[key_list[i]])):
                    cur_net_old = ok[j]
                    cur_net_new = nk[j]
                    if not (cur_net_new[1] == cur_net_old[1] and cur_net_new[4] == cur_net_old[4]):
                        flag = 1
                        outlist.append([flag, [key_list[i], (ok, nk)]])
        if flag == 0:
            return False
        else:
            return outlist

    def deposit_change_second(self):
        net_change = self.network_change()
        outlist = []
        flag = 0
        if not net_change == False:
            for i in range(len(net_change)):
                cur_change = net_change[i]
                flg, [key, (ok, nk)] = cur_change
                if flg == 11:
                    cur_key = nk
                if flg == 12:
                    cur_key = ok
                if flg != 2:
                    for j in range(len(cur_key)):
                        cur_new = nk[j]
                        cur_old = ok[j]
                        if not cur_old[4] == cur_new[4]:
                            flag = 1
                            outlist.append([flag, [key, (ok, nk)]])
                        break
        if flag == 0:
            return False
        else:
            return outlist

    def deposit_change(self):
        outlist1 = self.deposit_change_first()
        outlist2 = self.deposit_change_second()
        outlist = []
        if not outlist1 == False:
            outlist += outlist1
        if not outlist2 == False:
            outlist += outlist2
        if len(outlist) > 0:
            return outlist
        else:
            return False


"""
а) appear_or_disappear() - возврещает cписок следующего формата:
[флаг, (исчезнувшие, монеты, появившиеся монеты), список ключей, которые и были, и остались]
если изменений нет, то возвращает: [False, (False, False), список ключей, которые и были, и остались]
б)Output().network_change() - возвращает список, каждый элемент которого имеет следующий формат:
 [flag, [название монеты, (старые данные по этой монете, новые данные по этой монете)]],
 где flag=11 - исчезновенее сетей(и)
     flag=12 - появление новых сетей(и)
     flag=2 - изменение статуса сети
     Если список пустой, возвразщается False
     
     
!!!! Вместо import XXX в начаеле файла необходимо прописать:
from {файл, где находится конфиг бота} import {словарь c предыдущими значениями} as saved_data 
"""
