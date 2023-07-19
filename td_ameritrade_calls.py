import requests
import json
import Constants.constants as constants
import datetime

# Getters

# Gets Quotes for a list of tickers, one API call
def getQuotes(tickers):
    endpoint = "https://api.tdameritrade.com/v1/marketdata/quotes"
    page = requests.get(url=endpoint,
        params={'apikey' : constants.CONSUMER_KEY, 'symbol': tickers})
    quotes = json.loads(page.content)   
    return quotes

def getHistoricals(asset):
    endpoint = "https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory"
    full_url = endpoint.format(ticker=asset)

    page = requests.get(url=full_url, 
            params={'apikey' : constants.CONSUMER_KEY, 
                    'periodType' : 'year',
                    'period' : str(constants.YEARS_BACK_HISTORICAL),
                    'frequencyType' : "daily",
                    'frequency' : '1',
                    'needExtendedHoursData' : 'false' })

    historicals = json.loads(page.content)["candles"]

    return historicals

def getMarketHours(date):
    # Note: I can change to look at other markets ['EQUITY', 'OPTIONS', 'FUTURE', 'BOND', 'FOREX']
    endpoint = "https://api.tdameritrade.com/v1/marketdata/EQUITY/hours"
    page = requests.get(url=endpoint,
                        params = {'apikey': constants.CONSUMER_KEY,
                                  'date': date})
    try:
        return json.loads(page.content)['equity']['EQ'] 
    except: 
        return json.loads(page.content)['equity']['equity'] 
    
def getOptionsContracts(asset):
    endpoint = "https://api.tdameritrade.com/v1/marketdata/chains"

    # Params
    contractType = "PUT"
    range = "OTM"
    today = datetime.date.today()
    week_from_now = today + datetime.timedelta(days=7)
    fromDate = today.strftime("%Y-%m-%d")
    toDate = week_from_now.strftime("%Y-%m-%d")
    
    page = requests.get(url=endpoint, 
            params={'apikey' : constants.CONSUMER_KEY, 
                    "symbol" : asset,
                    'contractType' : contractType,
                    'range': range,
                    "fromDate": fromDate,
                    "toDate": toDate })
    
    return json.loads(page.content)["putExpDateMap"]

def getMovers():
    endpoint = "https://api.tdameritrade.com/v1/marketdata/{index}/movers"
    full_url = endpoint.format(index="$SPX.X")

    page = requests.get(url=full_url, 
            params={'apikey' : constants.CONSUMER_KEY, 
                    'direction' : 'down',
                    'change' : 'percent'})
    print(json.loads(page.content))