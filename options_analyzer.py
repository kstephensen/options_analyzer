import requests
import json
import numpy as np
import datetime
import pandas as pd
import constants

## To-Do:
# Add method to check if the market is open
# Add method to get how much money is in my account -> recommend actions off of that amount
# Refresh my account
# Add ability to add or remove from my watchlist

# credit: https://medium.com/analytics-vidhya/an-introduction-to-the-td-ameritrade-api-in-python-8c9d462e966c


# Getters
def get_quotes(tickers):
    endpoint = "https://api.tdameritrade.com/v1/marketdata/quotes"
    page = requests.get(url=endpoint,
        params={'apikey' : constants.CONSUMER_KEY, 'symbol': tickers})
    quotes = json.loads(page.content)   
    return quotes

def get_historicals(asset):
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

    return pd.DataFrame(historicals)   

def get_std_dev(asset):
    # Get the standard deviation by week for the asset
    # for the last 2 years

    historicals = get_historicals(asset)

    returns = []

    for day in range(1, len(historicals.close)):
        day_return = historicals.close[day] - historicals.close[day-1]
        returns.append(day_return)
    
    return np.std(returns)

def get_options_actions(assets):
    # We need to get a list of all possible trades that gets us at 
    ## Strategy - 
    ### Pick trades that produce at least a 1% return
    ### Strike that is at least one std dev away (two is better)
    ### Only looking at weeklies

    endpoint = "https://api.tdameritrade.com/v1/marketdata/chains"
    ctrct = "PUT"
    rnge = "OTM"

    today = datetime.date.today()
    week_from_now = today + datetime.timedelta(days=7)

    fdate = today.strftime("%Y-%m-%d")
    tdate = week_from_now.strftime("%Y-%m-%d")

    options_actions = pd.DataFrame({'Ticker': [],
                                    'Strike Price' : [],
                                    'Premium': [],
                                    'Percent Return' : [],
                                    'Exp Date' : []
                                     })

    for asset in assets:
        ## Get Options contracts
        page = requests.get(url=endpoint, 
            params={'apikey' : constants.CONSUMER_KEY, 
                    "symbol" : asset,
                    'contractType' : ctrct,
                    'range': rnge,
                    "fromDate": fdate,
                    "toDate": tdate })
        contract_map = json.loads(page.content)["putExpDateMap"]


        for expiration_date in contract_map:
            for price in contract_map[expiration_date]:
                for contract in contract_map[expiration_date][price]:
                    premium = contract["ask"]
                    strike_price = contract["strikePrice"]
                    perc_return = premium / strike_price * 100
                    bidsize = contract["bidSize"]

                    if perc_return > constants.THRESHOLD_PERCENT_GAIN and premium * 100 > constants.THRESHOLD_PREMIUM_GAIN and bidsize > 0:
                        options_actions.loc[len(options_actions.index)] = [asset, strike_price, premium, perc_return, expiration_date]
    return options_actions

def get_watchlist():
    with open("watchlist.txt", "r") as file:
        watchlist = [line.rstrip() for line in file]
    return watchlist

# Evaluators
def eval_downdays(watchlist):
    ## Who is down
    # Need to stringify our watchlist
    tickers = str(watchlist)[1:-1].replace("'", "").replace(" ", "")
    # get quotes
    quotes = get_quotes(tickers)
    # see who all is down today
    downDays = {}
    for asset in quotes.keys():
        if quotes[asset]["netPercentChangeInDouble"] < constants.THRESHOLD_DOWN_DAY:
            downDays[asset] = {"price": quotes[asset]["lastPrice"],
                               "netChange": quotes[asset]["netPercentChangeInDouble"]}
    return downDays

def eval_options_actions(actions, asset_prices):
    # Evaluate options_actions 
    # get std_deviations
    asset_std_devs = {}
    for asset in asset_prices.keys():
        asset_std_devs[asset] = get_std_dev(asset)

    action_stds = []
    action_pos = []
    cur_prices = []
    for index, action in actions.iterrows():
        cur_asset = action["Ticker"]
        cur_std_dev = asset_std_devs[cur_asset]
        cur_strike = action["Strike Price"]
        cur_price = asset_prices[cur_asset]["price"]

        std_dev_pos = ""
        if cur_strike < cur_price - cur_std_dev:
            std_dev_pos += "*"
            if cur_strike < cur_price - 2 * cur_std_dev:
                std_dev_pos += "*"

        action_stds.append(cur_std_dev)
        action_pos.append(std_dev_pos)
        cur_prices.append(cur_price)

    actions["CurPrice"] = cur_prices
    actions["Std Dev"] = action_stds
    actions["Pos"] = action_pos
    

    print(actions.sort_values(by=["Exp Date", "Pos", "Percent Return"], ascending = False).to_string())

# Printers
def print_watchlist():
    print("Current Watchlist:")
    print(get_watchlist())

def print_options(df_options, assets_prices):
    pass

# This could probably be broken down more
def get_actions():
    watchlist = get_watchlist()
    # Get dictionary of current down day stocks and their current prices
    downDayWatchlist = eval_downdays(watchlist)
    print("These are all of the watchlist stocks down today: {}".format(list(downDayWatchlist.keys())))
    # evaluate this list by getting all options
    options_actions = get_options_actions(downDayWatchlist.keys())
    
    if len(options_actions.index) != 0:
        print("\nPossible Actions:")
        eval_options_actions(options_actions, downDayWatchlist)
        
    else:
        print("Looks like there aren't any actions! Check back in an hour or so.")

def add_watchlist():
    print("Edit List")

def get_asset_actions():
    asset = input("Asset to evaluate > ")
    quote = get_quotes(asset)
    
    asset_info = {}
    asset_info[asset] = {"price": quote[asset]["lastPrice"],
                        "netChange": quote[asset]["netPercentChangeInDouble"]}
    actions = get_options_actions([asset])
    eval_options_actions(actions, asset_info)

# GAME-PLAY

def menu():
    print()
    for option in APP_ACTIONS.keys():
        print("{}. {}".format(option, APP_ACTIONS[option]["description"]))

def greeting():
    print("Welcome Kasen!")

APP_ACTIONS = {
    "1": {"description": "Get watchlist actions",
        "function": get_actions},
    "2": {"description": "See watchlist",
        "function" : print_watchlist},
    "3": {"description": "Get single asset recommendations",
        "function": get_asset_actions},
    "q": {"description": "Quit"}
}

def main():
    greeting()
    playing = True

    while playing:
        menu()
        option = input("Select an option > ")
        while option.lower() not in APP_ACTIONS.keys():
            menu()
            print("Please enter a valid option")
            option = input("Select an option > ")
        
        if option.lower() != "q":
            APP_ACTIONS[option]["function"]()
        else: 
            print("Thank you!")
            playing = False

if __name__ == "__main__":
    main()


# print("[{:.2f} - {:.2f} - {:.2f}]".format(curPrice, curPrice - std_dev, curPrice - 2*std_dev ))