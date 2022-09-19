# implementation of modern portfolio theroy
import scipy as sci
import numpy as np
import pandas as pd
import datetime as dt
from pandas_datareader import data as pdr
import plotly.graph_objects as go
import plotly.offline as pyo
# import data

stockList = ["AAPL", "META", "AMZN", "XOM"]
endDate = dt.datetime.now()
startDate = endDate - dt.timedelta(days=365)


def getData(stocks, start, end):
    stockData = pdr.get_data_yahoo(stocks, start=start, end = end)
    stockData = stockData['Close']
    returns = stockData.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()
    return meanReturns, covMatrix

meanReturns, covMatrix = getData(stockList, start=startDate, end=endDate)

def portfolioPerformance(weights, meanReturns, covMatrix):
    returns = np.sum(meanReturns*weights)*252
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights))) * np.sqrt(252)
    return returns, std


def negativeSR(weights, meanReturns, covMatrix, riskFreeRate = 0):
    pReturns, pStd = portfolioPerformance(weights, meanReturns, covMatrix)
    return - (pReturns - riskFreeRate)/pStd 

def maxSR(meanReturns, covMatrix, riskFreeRate =0, constrainSet = (0,1)):
    "Minimise the negative SR, by altering the weights of the portfolio"
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix, riskFreeRate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constrainSet 
    bounds = tuple(bound for asset in range(numAssets))
    result = sci.optimize.minimize(negativeSR, numAssets*[1./numAssets], args= args, method = 'SLSQP', bounds = bounds, constraints= constraints)
    return result 

def portfolioVariance(weights, meanReturns, covMatrix):
    return portfolioPerformance(weights, meanReturns, covMatrix)[1]

def minimizeVariance(meanReturns, covMatrix, constrainSet = (0,1)):
    "minimize the portfolio variance by alering the weights/allocation of assets in the portfolio"
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constrainSet 
    bounds = tuple(bound for asset in range(numAssets))
    result = sci.optimize.minimize(portfolioVariance, numAssets*[1./numAssets], args= args, method = 'SLSQP', bounds = bounds, constraints= constraints)
    return result 


def portfolioReturns(weights, meanReturns, covMatrix):
    return portfolioPerformance(weights, meanReturns, covMatrix)[0]

def efficientOpt(meanReturns, covMatrix, returnTarget,  constrainSet = (0,1)):
    """For each returnTarget, we want to optimise the portfolio for min variance"""
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)
    
    constraints = ({'type': 'eq', 'fun': lambda x: portfolioReturns(x, meanReturns, covMatrix) - returnTarget}, {'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bound = constrainSet
    bounds = tuple(constrainSet for asset in range(numAssets))
    effOpt = sci.optimize.minimize(portfolioVariance, numAssets*[1./numAssets], args=args, method = 'SLSQP', bounds = bounds, constraints = constraints)
    return effOpt 


def calculatedResults(meanReturns, covMatrix, riskFreeRate = 0 , constrainSet = (0,1)):
    """ Read in mean, cov matrix, and other financial information output, Max SR, Min Volatility, efficient frontier """
    #Max Shaprt Ratio Portfolio
    maxSR_Portfolio = maxSR(meanReturns, covMatrix)
    maxSR_returns, maxSR_std = portfolioPerformance(maxSR_Portfolio['x'], meanReturns, covMatrix)
    maxSR_returns, maxSR_std = round(maxSR_returns*100, 2), round(maxSR_std*100, 2)
    maxSR_allocation = pd.DataFrame(maxSR_Portfolio['x'], index=meanReturns.index, columns = ['allocation'])
    maxSR_allocation.allocation = [round(i*100, 0) for i in maxSR_allocation.allocation]

    #Min Volatility Portfolio
    minVol_Portfolio = minimizeVariance(meanReturns, covMatrix)
    minVol_returns, minVol_std = portfolioPerformance(minVol_Portfolio['x'] , meanReturns, covMatrix)
    minVol_returns, minVol_std = round(minVol_returns*100, 2), round(minVol_std*100, 2)
    minVol_allocation = pd.DataFrame(minVol_Portfolio['x'], index=meanReturns.index, columns = ['allocation'])
    minVol_allocation.allocation = [round(i*100, 0) for i in minVol_allocation.allocation]
    
    #efficient frontier
    efficientList = []
    targetReturns = np.linspace(minVol_returns, maxSR_returns, 20)
    for target in targetReturns:
        efficientList.append(efficientOpt(meanReturns, covMatrix, target)['fun'])

    return maxSR_returns, maxSR_std, maxSR_allocation, minVol_returns, minVol_std, minVol_allocation, efficientList, targetReturns

def EF_graph(meanReturns, covMatrix, riskFreeRate =0 , constrainSet = (0,1)):
    """return a graph ploting the min vol, max sr, and efficient frontier"""
    maxSR_returns, maxSR_std, maxSR_allocation, minVol_returns, minVol_std, minVol_allocation, efficientList, targetReturns = calculatedResults(meanReturns, covMatrix, riskFreeRate = 0 , constrainSet = (0,1))

    #Max SR
    MaxSharpeRatio = go.Scatter( 
                name = 'Maximum Sharpe Ratio',
                mode = 'markers',
                x=[maxSR_std],
                y=[maxSR_returns],
                marker = dict(color='red', size= 14, line=dict(width=3, color='black'))
    )

    #min Vol
    MinVol = go.Scatter( 
                name = 'Minimum Volatility',
                mode = 'markers',
                x=[minVol_std],
                y=[minVol_returns],
                marker = dict(color='green', size= 14, line=dict(width=3, color='black'))
    )

    # Efficient frontier

    EF_curve = go.Scatter( 
                name= 'Efficient Frontier',
                mode= 'lines',
                x=[round(ef_std*100, 2) for ef_std in efficientList],
                y=[round(target*100, 2) for target in targetReturns],
                line=dict(color='black', width=4, dash='dashdot')
    )

    data = [MaxSharpeRatio, MinVol, EF_curve]

    layout = go.Layout( 
                title = 'Portfolio Optimisation with Efficient Frontier',
                yaxis = dict(title = 'Annualised return (%)'),
                xaxis = dict(title= 'Annualised Volatility (%)'),
                showlegend= True,
                legend= dict(x = 0.75, y = 0, traceorder = 'normal',
                            bgcolor = '#E2E2E2',
                            bordercolor = 'black',
                            borderwidth = 2),
                width=800,
                height=600)

    fig = go.Figure(data = data, layout = layout)
    return fig.show()

EF_graph(meanReturns, covMatrix)



