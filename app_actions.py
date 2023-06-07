from td_ameritrade_calls import *
import numpy as np
import pandas as pd
import time
from tqdm import tqdm
import math

###### Helpers ######
def get_watchlist():
    with open("watchlist.txt", "r") as file:
        watchlist = [line.rstrip() for line in file]
    return watchlist

def get_std_dev_and_mean(asset):
    # Get the standard deviation by week for the asset
    # for the last 3 years
    historicals = pd.DataFrame(getHistoricals(asset))
    # historicals['date'] = pd.to_datetime(historicals.datetime, unit='ms').dt.date
    today = datetime.date.today()
    period = 5 - today.weekday()
    closing_prices = historicals['close'].to_numpy()
    # Use array broadcasting rather than brute force
    returns = (closing_prices[1:] - closing_prices[:-1]) / closing_prices[:-1]
    return [np.std(returns) * math.sqrt(period), np.mean(returns)]

## Context:
# {'asset': {'price': XX,
#            'netChange': XX}}
def get_watchlist_down_days():
    print("Getting Watchlist Subset...")
    watchlist = get_watchlist()
    ## Who is down
    # Need to stringify our watchlist
    tickers = str(watchlist)[1:-1].replace("'", "").replace(" ", "")
    # get quotes (only one API call)
    quotes = getQuotes(tickers)
    # see who all is down today
    downDays = {}
    for asset in tqdm(quotes.keys()):
        if quotes[asset]["netPercentChangeInDouble"] < constants.THRESHOLD_DOWN_DAY:
            [std_dev, mean] = get_std_dev_and_mean(asset)

            downDays[asset] = {"price": quotes[asset]["lastPrice"],
                               "netChange": quotes[asset]["netPercentChangeInDouble"],
                               'stdDev': std_dev,
                               'mean': mean
                               }
    return downDays

def eval_options_actions(actions, asset_prices):
    # Evaluate options_actions 
    # get std_deviations
    # asset_std_devs = {}
    # for asset in asset_prices.keys():
    #     asset_std_devs[asset] = get_std_dev(asset)

    action_stds = []
    action_pos = []
    cur_prices = []
    current_price_strike_difference = []
    # means = []
    for index, action in actions.iterrows():
        cur_asset = action["Ticker"]
        cur_std_dev = asset_prices[cur_asset]['stdDev']
        cur_strike = action["Strike Price"]
        cur_price = asset_prices[cur_asset]["price"]
        cur_difference = cur_price - cur_strike
        # cur_mean = asset_prices[cur_asset]["mean"]
        std_dev_pos = ""
        if cur_strike <= cur_price * (1 - cur_std_dev):
            std_dev_pos += "*"
            if cur_strike <= cur_price * (1 - 2 * cur_std_dev):
                std_dev_pos += "*"

        action_stds.append(cur_std_dev)
        action_pos.append(std_dev_pos)
        cur_prices.append(cur_price)
        current_price_strike_difference.append(cur_difference)
        # means.append(cur_mean)

    actions["CurPrice"] = cur_prices
    actions["Std Dev"] = action_stds
    actions["Difference"] = current_price_strike_difference
    # actions["Mean"] = means
    actions["Pos"] = action_pos
    
    print(actions.sort_values(by=["Exp Date", "Pos", "Percent Return"], ascending = False).to_string())

# Takes in an array of tickers
def get_options_actions(assets):
    # We need to get a list of all possible trades that gets us at 
    ## Strategy - 
    ### Pick trades that produce at least a 1% return
    ### Strike that is at least one std dev away (two is better)
    ### Only looking at weeklies
    print()
    print("Getting Options...")
    options_actions = pd.DataFrame({'Ticker': [],
                                    'Strike Price' : [],
                                    'Premium': [],
                                    'Percent Return' : [],
                                    'Exp Date' : []
                                     })

    for asset in tqdm(assets):
        ## Get options contracts
        contract_map = getOptionsContracts(asset)
        
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

###### APP Actions #####
# This could probably be broken down more
def get_actions():
    # Get dictionary of current down day stocks and their current prices
    downDayWatchlist = get_watchlist_down_days()
    print()
    print("Here are all of the watchlist stocks down today: {}".format(list(downDayWatchlist.keys())))
    
    # evaluate this list by getting all options
    options_actions = get_options_actions(downDayWatchlist.keys())
    # We're essentially making three calls per asset

    if len(options_actions.index) != 0:
        print("\nPossible Actions:")
        eval_options_actions(options_actions, downDayWatchlist)
        
    else:
        print("Looks like there aren't any actions! Check back in an hour or so.")

def print_watchlist():
    print("Current Watchlist:")
    print(get_watchlist())

def get_asset_actions():
    asset = input("Asset to evaluate > ")
    quote = getQuotes(asset)
    
    asset_info = {}
    asset_info[asset] = {"price": quote[asset]["lastPrice"],
                        "netChange": quote[asset]["netPercentChangeInDouble"]}
    actions = get_options_actions([asset])
    eval_options_actions(actions, asset_info)
