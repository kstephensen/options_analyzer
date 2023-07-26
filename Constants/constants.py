import Constants.api_key as api_key

CONSUMER_KEY = api_key.CONSUMER_KEY

THRESHOLD_DOWN_DAY = 0
# Will only look at actions that give me a gain of 0.5% or more
THRESHOLD_PERCENT_GAIN = 0.7
# We will only consider premiums of $20 or more
THRESHOLD_PREMIUM_GAIN = 10
# How many years back do we want to get data for standard deviation
YEARS_BACK_HISTORICAL = 3
# What period do we want to calculate standard deviation? (in days)
STANDARD_DEVIATION_PERIOD = 5