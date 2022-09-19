# implementation of modern portfolio theroy

import numpy as np
import datetime as dt
from pandas_datareader import data as pdr

# import data

def getData(stocks, start, end):
    stockData = pdr.get_data_yahoo(stocks, start=start, end = end)
    stockData = stockData['Close']
    returns = stockData.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()
    return meanReturns, covMatrix

def portfolioPerformance(weights, meanReturns, covMatrix):
    returns = np.sum(meanReturns*weights)*252
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights))) * np.sqrt(252)
    return returns, std
stockList = ["AAPL", "META", "AMZN", "XOM"]

endDate = dt.datetime.now()
startDate = endDate - dt.timedelta(days=365)

weights = np.array([0.25, 0.25, 0.25, 0.25])

meanReturns, covMatrix = getData(stockList, start=startDate, end=endDate)
returns, std = portfolioPerformance(weights, meanReturns, covMatrix)
print(round(returns*100,2), round(std*100, 2))