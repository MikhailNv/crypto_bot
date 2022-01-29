import requests, json, hashlib, hmac, config

class Loginer():
    def __init__(self):
        self.servertime = requests.get("https://api.binance.com/api/v1/time")
        self.servertimeobj = json.loads(self.servertime.text)
        self.servertimeobj = self.servertimeobj['serverTime']

    def login(self):
        queryString = 'timestamp='+str(self.servertimeobj)
        signature = hmac.new(config.apiSecret.encode('utf-8'), queryString.encode('utf-8'), hashlib.sha256).hexdigest()
        session = requests.get('https://api.binance.com/sapi/v1/capital/config/getall',
                            params={
                                "timestamp": self.servertimeobj,
                                "signature": signature,
                            },
                            headers={'X-MBX-APIKEY': config.apiKey})
        return json.loads(session.text)

class Parser(Loginer):
    def __init__(self):
        Loginer.__init__(self)
        self.info_about_coins = self.login()

    def parsers(self):
        list_of_coins = []
        for dict in range(len(self.info_about_coins)):
            coin = self.info_about_coins[dict]['coin']
            list_of_coins.append(["Крипта: "+coin])
            for net in range(len(self.info_about_coins[dict]['networkList'])):
                network = self.info_about_coins[dict]['networkList'][net]['network']
                withdrawEnable = self.info_about_coins[dict]['networkList'][net]['withdrawEnable']
                list_of_coins[dict].append(["Сеть: "+network, "Открыта" if withdrawEnable == True else "Закрыта"])
        return list_of_coins

parser1 = Parser().parser()
#for i in range (len(parser1)):
    #print(parser1[i])
