from statistics import median_grouped
from turtle import st
import pandas as pd
import numpy as np
import datetime as dt
from pandas_datareader import data as pdr
from scipy.stats import norm, t

def getData(stocks, start, end):
    stockData = pdr.get_data_yahoo(stocks, start = start, end = end)
    stockData = stockData['Close']
    returns = stockData.pct_change()
    meanReturns = returns.mean()
    covMatrix = returns.cov()
    return returns, meanReturns, covMatrix

#Portfolio Performance

def portfolioPerformance(weights, meanReturns, covMatrix, Time):
    returns = np.sum(meanReturns*weights)*Time
    std = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))* np.sqrt(Time)
    return returns, std

stocklist = ['CBA', 'BHP', 'TLS', 'NAB', 'WBC', 'STO']
stocks = [ stock + '.AX' for stock in stocklist]
endDate = dt.datetime.now()
startDate = endDate - dt.timedelta(days =800)

returns, meanReturns, covMatrix = getData(stocks, start=startDate, end=endDate)
returns = returns.dropna() 

weights = np.random.random(len(returns.columns))
weights /= np.sum(weights) 

returns['portfolio'] = returns.dot(weights)
print(returns) 

def historicalVaR(returns, alpha=5):
    """
    Read in a pandas dataframe of returns/ a pandas series of returns
    output the percentile of the distributionat the given alpha confidence level    """
    if isinstance(returns, pd.Series):
        return np.percentile(returns, alpha)

    # A passed user-defined-function will be passed a Series for evaluation

    elif isinstance(returns, pd.DataFrame):
        return returns.aggregate(historicalVaR, alpha =5)
    
    else:
        raise TypeError("Expected returns to be dataframe or series")

def historicalCVaR(returns, alpha=5):
    if isinstance(returns, pd.Series):
        belowVaR = returns <= historicalVaR(returns, alpha=alpha)
        return returns[belowVaR].mean()

        # A passed user-defined-function will be passed a Series for evaluation

    elif isinstance(returns, pd.DataFrame):
        return returns.aggregate(historicalCVaR, alpha =5)
        
    else:
        raise TypeError("Expected returns to be dataframe or series")

# 1day

Time = 1
VaR = historicalVaR(returns['portfolio'], alpha =5)*np.sqrt(Time)
CVaR = historicalCVaR(returns['portfolio'], alpha = 5)*np.sqrt(Time)
pRet, pStd = portfolioPerformance(weights, meanReturns, covMatrix, Time)

InitialInvestment = 100000
print('expected portfolio return" ', round(InitialInvestment*pRet, 2))
print('value at risk at 95 CI is" ', round(InitialInvestment*VaR, 2))
print('conditional value at risk at 95 CI is" ', round(InitialInvestment*CVaR, 2))

def var_parametric(portfolioReturn, portfolioStd, distribution='normal', alpha = 5, dof=6):
    """"Calculate the portfolio VaR given a distribution, with known parameters"""
    if distribution == 'normal':
        VaR = norm.ppf(1-alpha/100)*portfolioStd - portfolioReturn
    elif distribution == 't-distribution':
        nu = dof
        VaR = np.sqrt((nu-2)/(nu)) * t.ppf(1-alpha/100, nu)*portfolioStd - portfolioReturn
    else:
        TypeError("Expected distribution to be normal or t")
    return VaR 

def cvar_parametric(portfolioReturn, portfolioStd, distribution='normal', alpha = 5, dof=6):
    """"Calculate the portfolio VaR given a distribution, with known parameters"""
    if distribution == 'normal':
        CVaR = (alpha/100)**-1*norm.pdf(norm.ppf(alpha/100))*portfolioStd - portfolioReturn
    elif distribution == 't-distribution':
        nu = dof
        x_anu = t.ppf(alpha/100, nu)
        CVaR = -1/(alpha/100)*(1-nu)**-1 * (nu-2 + x_anu**2) * t.pdf(x_anu, nu)*portfolioStd - portfolioReturn 
    else:
        TypeError("Expected distribution to be normal or t")
    return CVaR 

normVar = var_parametric(pRet, pStd)
normCVar =cvar_parametric(pRet, pStd)

tVar = var_parametric(pRet, pStd, distribution='t-distribution')
tCVar =cvar_parametric(pRet, pStd, distribution='t-distribution')

print('normal var" ', round(InitialInvestment*normVar, 2))
print('normal cvar" ', round(InitialInvestment*normCVar, 2))
print('t Var" ', round(InitialInvestment*tVar, 2))
print('t CVar" ', round(InitialInvestment*tCVar, 2))