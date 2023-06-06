import datetime
from td_ameritrade_calls import getMarketHours
from app_actions import get_actions, print_watchlist, get_asset_actions

## To-Do:
# [DONE] Add method to check if the market is open
# Add method to get how much money is in my account -> recommend actions off of that amount
# Refresh my account
# credit: https://medium.com/analytics-vidhya/an-introduction-to-the-td-ameritrade-api-in-python-8c9d462e966c

APP_ACTIONS = {
    "1": {"description": "Get watchlist actions",
        "function": get_actions},
    "2": {"description": "See watchlist",
        "function" : print_watchlist},
    "3": {"description": "Get single asset recommendations",
        "function": get_asset_actions},
    "q": {"description": "Quit"}
}

# Prints the menu and options
def menu():
    print()
    for option in APP_ACTIONS.keys():
        print("{}. {}".format(option, APP_ACTIONS[option]["description"]))

# Prints a greeting and the market close time
def greeting():
    print("Welcome Kasen!")
    # Alert if market is open and what time it closes
    market_hours = getMarketHours(datetime.date.today())
    marketIsOpen = market_hours['isOpen']
    if marketIsOpen:
        closing_time = market_hours['sessionHours']['regularMarket'][0]['end'].split('T')[1].split('-')[0]
        print("The markets are open and close at {} ET".format(closing_time))
    else: 
        print("The markets are closed.")

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