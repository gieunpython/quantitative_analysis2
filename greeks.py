from py_vollib.black_scholes import black_scholes as bs
from py_vollib.black_scholes.greeks.analytical import delta, gamma, vega, theta, rho

import numpy as np
from scipy.stats import norm


r = 0.01
S = 30
K = 40
T = 240/365
sigma = 0.30

def blackScholes(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if type == "c":
            price = S*norm.cdf(d1, 0 ,1) - K*np.exp(-r*T)*norm.cdf(d2, 0 ,1)
        elif type == "p":
            price = K*np.exp(-r*T)*norm.cdf(-d2, 0, 1) - S*norm.cdf(-d1, 0, 1)
        return price, bs(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")

print("Option price is: ", blackScholes(r, S, K, T, sigma, "c"))

# Delta Calculation
def delta_calc(r, S, K, T, sigma, type="c"):
    "Calculate delta of an option"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    try:
        if type == "c":
            delta_calc = norm.cdf(d1, 0 ,1) 
        elif type == "p":
            delta_calc = -norm.cdf(-d1, 0 ,1) 
        return delta_calc, delta(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")

# Gamma

def gamma_calc(r, S, K, T, sigma, type="c"):
    "Calculate Gamma of an option"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    try:
        gamma_calc = norm.pdf(d1, 0 ,1)/(S*sigma*np.sqrt(T))
        return gamma_calc, gamma(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")


# Vega

def vega_calc(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    try:
        vega_calc = S*norm.pdf(d1, 0 ,1)*np.sqrt(T)
        return vega_calc*0.01, vega(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")

def theta_calc(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if type == "c":
            theta_calc = -S*norm.pdf(d1, 0 ,1)*sigma/(2*np.sqrt(T)) - r*K*np.exp(-r*T)*norm.cdf(d2, 0 ,1)
        elif type == "p":
            theta_calc = -S*norm.pdf(d1, 0 ,1)*sigma/(2*np.sqrt(T)) + r*K*np.exp(-r*T)*norm.cdf(-d2, 0 ,1)
        return theta_calc/365, theta(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")


def rho_calc(r, S, K, T, sigma, type="c"):
    "Calculate BS price of call/put"
    d1 = (np.log(S/K) + (r + sigma**2/2)*T)/(sigma*np.sqrt(T))
    d2 = d1 - sigma*np.sqrt(T)
    try:
        if type == "c":
            rho_calc = K*T*np.exp(-r*T)*norm.cdf(d2, 0 ,1)
        elif type == "p":
            rho_calc = -K*T*np.exp(-r*T)*norm.cdf(-d2, 0 ,1)
        return rho_calc*0.01, rho(type, S, K, T, r, sigma)
    except:
        print("please confirm option type, either 'c' for call or 'p' for put")


option_type='p'
print("Option Price: ", [round(x,3) for x in blackScholes(r, S, K, T, sigma, option_type)])
print("       Delta: ", [round(x,3) for x in delta_calc(r, S, K, T, sigma, option_type)])
print("       Gamma: ", [round(x,3) for x in gamma_calc(r, S, K, T, sigma, option_type)])
print("       Vega : ", [round(x,3) for x in vega_calc(r, S, K, T, sigma, option_type)])
print("       Theta: ", [round(x,3) for x in theta_calc(r, S, K, T, sigma, option_type)])
print("       Rho  : ", [round(x,3) for x in rho_calc(r, S, K, T, sigma, option_type)])