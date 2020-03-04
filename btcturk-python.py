import base64
import hashlib
import hmac
import requests
import json

API_KEY = your_api_key
API_SECRET = your_api_secret_key

def authenticate():
    public_key = API_KEY
    private_key = API_SECRET
    private_key = base64.b64decode(private_key)
    stamp = str(int(time.time())*1000)
    data = "{}{}".format(public_key , stamp).encode('utf-8')
    signature = hmac.new(private_key , data , hashlib.sha256).digest()
    signature = base64.b64encode(signature)
    headers = {"X-PCK":public_key , "X-Stamp":stamp , "X-Signature":signature , "Content-Type":"application/json"}
    return headers


def getexchangeInfo():
    url = "https://api.btcturk.com/api/v2/server/exchangeinfo"
    headers = {"Content-Type":"application/json"}
    params = {}
    resp = requests.get(url=url , headers=headers , params=params)
    result = resp.json()
    if result['success'] == True:
        with open('exchangeinfo.txt' , 'w') as outfile:
            json.dump(result['data'] , outfile , indent=2)


def readexchangeInfo(pairSymbol=None):
    result = {}
    excinfo = Path("exchangeinfo.txt")
    if excinfo.is_file():
        with open('exchangeinfo.txt') as json_file:
            data = json.load(json_file)
    else:
        getexchangeInfo()
        with open('exchangeinfo.txt') as json_file:
            data = json.load(json_file)
    if data['serverTime'] != '':
        result['serverTime'] = data['serverTime']
        stime = data['serverTime']
        ctime = int(time.time()*1000)
        diff = ctime - stime
        if int(diff/1000) > 60*60:
            getexchangeInfo()
            with open('exchangeinfo.txt') as json_file:
                data = json.load(json_file)
                result['serverTime'] = data['serverTime']
            
    if pairSymbol == '':
        found = 0
    else:
        found = 1
    
    if data['serverTime'] != '':
        for dataType in data:
            if dataType == "symbols":
                for curr in data['symbols']:
                    if curr['name'] == pairSymbol:
                        result['pairSymbol'] = curr['name']
                        result['status'] = curr['status']
                        result['numeratorScale'] = curr['numeratorScale']
                        result['denominatorScale'] = curr['denominatorScale']
                        result['hasFraction'] = curr['hasFraction']
                        result['minPrice'] = curr['filters'][0]['minPrice']
                        result['maxPrice'] = str(curr['filters'][0]['maxPrice'])
                        result['minExchangeValue'] = str(curr['filters'][0]['minExchangeValue'])
                        result["orderMethods"] = []
                        for x in range(len(curr['orderMethods'])):
                            result["orderMethods"] += [ curr["orderMethods"][x] ]
                        found = 2
                        break
            elif dataType == "currencies":
                for asset in data['currencies']:
                    if asset['symbol'] == pairSymbol:
                        result['pairSymbol'] = asset['symbol']
                        result['precision'] = str(asset['precision'])
                        found = 2
                        break
        if found == 2:
            return result
        elif found == 1:
            result['message'] = "pair or asset not found"
            return result
        else:
            return json.dumps(data , indent=2)
    else:
        result['message'] = "data source not available"
        return result


def checkBalances(pairSymbol = None , format = "json"):
    url = "https://api.btcturk.com/api/v1/users/balances"
    params = {}
    resp = requests.get(url=url , headers=authenticate() , params=params)
    result = resp.json()
    if result['success'] is True:
        if len(result["data"]) > 0:
            if pairSymbol != "":
                if format == "raw":
                    print(result["data"])
                elif format == "json":
                     rtrn = json.dumps(result["data"] , indent=2)
            else:
                for assetID in range(len(result["data"])):
                    if pairSymbol != '' and pairSymbol == result["data"][assetID]['asset']:
                        totalBalance = "{:.8f}".format(float(result["data"][assetID]['balance']))
                        inOrderBalance = "{:.8f}".format(float(result["data"][assetID]['locked']))
                        freeBalance = "{:.8f}".format(float(result["data"][assetID]['free']))
                        rtrn = "%s" %("Asset:") , pairSymbol , "%s" %("totalBalance:") , totalBalance , "%s" %("Balance in Order:") , inOrderBalance , "%s" %("freeBalance:") , freeBalance
         return rtrn


def getQuantityScale(pairSymbol):
    url = "https://api.btcturk.com/api/v2/server/exchangeinfo"
    headers = {"Content-Type":"application/json"}
    params = {}
    resp = requests.get(url=url , headers=headers , params=params)
    result = resp.json()
    if result['success'] == True:
        if len(result['data']['symbols']) > 0:
            for assetID in range(len(result['data']['symbols'])):
                if pairSymbol != '' and pairSymbol == result['data']['symbols'][assetID]['name']:
                    numeratorScale = result['data']['symbols'][assetID]['numeratorScale']
                    return numeratorScale


def deleteOrder(orderId):
    url = "https://api.btcturk.com/api/v1/order"
    params = {"id":orderId}
    resp = requests.delete(url=url , headers=authenticate() , params=params)
    result = resp.json()
    if result['success'] == True:
        rtrn = "Order %s Deleted" %(orderId)
        return rtrn
    else:
        rtrn = "Error: %s" %(result["message"])
        return rtrn


def createOrder(pairSymbol , price , quantity , orderType , orderMethod , stopPrice):
    url = "https://api.btcturk.com/api/v1/order"
    params = {"pairSymbol":pairSymbol , "price":price , "quantity":quantity , "orderType":orderType , "orderMethod":orderMethod , "stopPrice":stopPrice , "newOrderClientId":"OnurPyBot"}
    resp = requests.post(url=url , headers=authenticate() , json=params)
    result = resp.json()
    if result["success"] is True:
        return result["data"]["id"]
    else:
        rtrn = "Error: %s" %(result["message"])
        return rtrn


def checkOpenOrders(pairSymbol):
    url = "https://api.btcturk.com/api/v1/openOrders"
    params = { "pairSymbol" : pairSymbol }
    resp = requests.get(url=url , headers=authenticate() , params=params)
    result = resp.json()
    
    o_Order = []
    reto = int(0)
    if len(result['data']['asks']) > 0:
        for askID in range(len(result['data']['asks'])):
            o_Order  += [result['data']['asks'][askID] ]
    
    if len(result['data']['bids']) > 0:
        for bidID in range(len(result['data']['bids'])):
            o_Order  += [ result['data']['bids'][bidID] ]
    
    if len(o_Order) > 0:
        return o_Order
    else:
        return ""


def orderBook(pairSymbol , limit = 10, prnt = None):
    url = "https://api.btcturk.com/api/v2/orderBook"
    headers = {"Content-Type":"application/json"}
    params = {"pairSymbol":pairSymbol , "limit":limit}
    resp = requests.get(url=url , headers=headers , params=params)
    data = resp.json()
    if data['success'] == True:
        if prnt == 1:
            bids = data['data']["bids"]
            asks = data['data']["asks"]
            print("\n======== BIDS ================= ASKS ======== %s" %(strftime("%Y-%m-%d %H:%M:%S" , time.localtime())))
            for x in range(len(bids)):
                print(bids[x][1] , "@" , bids[x][0] , "vs." , asks[x][0] , "@" , asks[x][1])
        else:
            return data['data']
    else:
        return data['message']


def userTransactions(numerator = None , denominator = None, t_type = None , s_date = None , e_date = None):
    if s_date is None:
        s_date = str((int(time.time()) - (60*60*24*1)) * 1000)
    if e_date is None:
        e_date = str(int((time.time()*1000)))
    url = "https://api.btcturk.com/api/v1/users/transactions/trade"
    #params = {"type":"sell" , "symbol":"btc"}
    params = {}
    if t_type == 'buy':
        params["type"] = "buy"
    elif t_type == 'sell':
        params["type"] = "sell"
    elif t_type == 'all':
        params["type"] = {"buy", "sell"}
    if numerator is not None and len(numerator) > 0 and numerator != "all":
        params["symbol"] = numerator
    elif numerator is not None and len(numerator) > 0 and numerator == "crypto":
        params["symbol"] = "btc"
        params["symbol"] = "usdt"
    elif numerator is not None and len(numerator) > 0 and numerator == "all":
        params["symbol"] = "btc"
        params["symbol"] = "usdt"
        params["symbol"] = "try"
    if s_date is not None and len(s_date) > 0:
        params["startDate"] = s_date
    if e_date is not None and len(e_date) > 0:
        params["endDate"] = e_date
    resp = requests.get(url=url , headers=authenticate() , params=params)
    data = resp.json()
    result = []
    if data["success"] == True:
        for t in range(len(data["data"])):
            if numerator != "all" and numerator != "crypto":
                if data["data"][t]["numeratorSymbol"] == numerator and data["data"][t]["denominatorSymbol"] == denominator:
                    result += [ data["data"][t] ]
            elif numerator == "crypto":
                if (data["data"][t]["numeratorSymbol"] == "BTC" or data["data"][t]["numeratorSymbol"] == "USDT") and data["data"][t]["denominatorSymbol"] == denominator:
                    result += [ data["data"][t] ]
            elif numerator == "all":
                if data["data"][t]["denominatorSymbol"] == denominator:
                    result += [ data["data"][t] ]
            else:
                result += [ data["data"][t] ]

        return result
    else:
        return data["message"]


def ticker(pairSymbol = None):
    url = "https://api.btcturk.com/api/v2/ticker"
    headers = {"Content-Type":"application/json"}
    if pairSymbol is not None:
        params = {"pairSymbol":pairSymbol}
        resp = requests.get(url=url , headers=headers , params=params)
    else:
        resp = requests.get(url=url , headers=headers)
    result = resp.json()
    if result["success"] == True:
        return result["data"]


def ohlc(pairSymbol = "BTC_TRY" , startDate=None , endData=None , what=None):
    url = "https://api.btcturk.com/api/v2/ohlc"
    headers = {"Content-Type":"application/json"}
    params = {"pairSymbol":pairSymbol}
    resp = requests.get(url=url , headers=headers , params=params)
    result = resp.json()
    if result["success"] == True:
        ohlcData = []
        if startDate != None:
            for data in result["data"]:
                ohlcData += [{ "time":data["time"] }]
        else:
            for data in result["data"]:
                hrTimestamp = data["time"] / 1000
                hrTimestamp = time.strftime("%d.%m.%Y" , time.localtime(hrTimestamp))
                ohlcData += [{ "date":hrTimestamp , "open":data["open"] , "high":data["high"] , "close":data["close"] , "average":data["average"] }]
        return ohlcData
        #return result["data"]


def allOrders(pairSymbol = None , orderStatus = None , limit = 1000 , orderid = None , startDate = None , endDate = None, page = 1):
    url = "https://api.btcturk.com/api/v1/allOrders"
    params = {}
    if pairSymbol is not None and len(pairSymbol) > 0:
        params["pairSymbol"] = pairSymbol
    else:
        params["pairSymbol"] = "BTC_TRY"

    if orderid is not None and orderid > 0:
        params["orderId"] = orderid
    else:
        if limit > 0 and limit <= 1000:
            rlimit = limit
        else:
            rlimit = 1000
        params["limit"] = rlimit
    
    if isinstance(page,int) == True and page > 1 and limit < 1000:
        params["page"] = page

    resp = requests.get(url=url , headers=authenticate() , params=params)
    result = resp.json()
    if result['success'] == True:
        quantityScale = readexchangeInfo(pairSymbol)['numeratorScale']
        allOrders = []
        c = 0
        for x in range(len(result["data"])):
            if isinstance(orderStatus, set) == True and result["data"][x]["status"] in orderStatus:
                c += 1
                allOrders += [{ "id":result["data"][x]["id"] , "price":result["data"][x]["price"] , "quantity":result["data"][x]["quantity"] , "stopPrice":result["data"][x]["stopPrice"] , "pair":result["data"][x]["pairSymbolNormalized"] , "type":result["data"][x]["type"] , "method":result["data"][x]["method"] , "time":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["time"] / 1000)) , "orderTimestamp" : result["data"][x]["time"] , "updateTime":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["updateTime"] / 1000)) , "updateTimestamp" : result["data"][x]["updateTime"] , "leftAmount":"{:.{quantityScale}f}".format(float(result["data"][x]["leftAmount"]) , quantityScale=quantityScale) , "status":result["data"][x]["status"] }]
                if c == limit:
                    break
            elif isinstance(orderStatus, set) == False and orderStatus is not None and len(orderStatus) > 0 and result["data"][x]["status"] == orderStatus:
                c += 1
                allOrders += [{ "id":result["data"][x]["id"] , "price":result["data"][x]["price"] , "quantity":result["data"][x]["quantity"] , "stopPrice":result["data"][x]["stopPrice"] , "pair":result["data"][x]["pairSymbolNormalized"] , "type":result["data"][x]["type"] , "method":result["data"][x]["method"] , "time":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["time"] / 1000)) , "orderTimestamp" : result["data"][x]["time"] , "updateTime":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["updateTime"] / 1000)) , "updateTimestamp" : result["data"][x]["updateTime"] , "leftAmount":"{:.{quantityScale}f}".format(float(result["data"][x]["leftAmount"]) , quantityScale=quantityScale) , "status":result["data"][x]["status"] }]
                if c == limit:
                    break
            elif (orderStatus is None or orderStatus == "") and len(orderStatus) == 0:
                c += 1
                allOrders += [{ "id":result["data"][x]["id"] , "price":result["data"][x]["price"] , "quantity":result["data"][x]["quantity"] , "stopPrice":result["data"][x]["stopPrice"] , "pair":result["data"][x]["pairSymbolNormalized"] , "type":result["data"][x]["type"] , "method":result["data"][x]["method"] , "time":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["time"] / 1000)) , "orderTimestamp" : result["data"][x]["time"] , "updateTime":time.strftime("%d.%m.%Y %H:%M:%S" , time.localtime(result["data"][x]["updateTime"] / 1000)) , "updateTimestamp" : result["data"][x]["updateTime"] , "leftAmount":"{:.{quantityScale}f}".format(float(result["data"][x]["leftAmount"]) , quantityScale=quantityScale) , "status":result["data"][x]["status"] }]
                if c == limit:
                    break
        return allOrders
    else:
        return result["message"]  
