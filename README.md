# Options Analyzer
Decision enhancer for selling puts on options based on a watchlist of stocks.

1. Checks all watchlist stocks that are having "down days"
2. Pulls all options for valid stocks fit specific strategy criteria (see Constants)
3. Calculates risk metrics (standard deviation, etc.)
4. Prioritizes options by percent return
