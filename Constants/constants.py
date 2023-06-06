import Constants.consumer_key as consumer_key

CONSUMER_KEY = consumer_key.CONSUMER_KEY

THRESHOLD_DOWN_DAY = 0
# Will only look at actions that give me a gain of 0.5% or more
THRESHOLD_PERCENT_GAIN = 0.8
# We will only consider premiums of $20 or more
THRESHOLD_PREMIUM_GAIN = 15
# How many years back do we want to get data for standard deviation
YEARS_BACK_HISTORICAL = 3