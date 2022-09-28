# Importing Necessary Modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import datetime as dt

# Importing Exchange Rate
start_date = dt.datetime.now()- dt.timedelta(days=2000) 
end_date = dt.datetime.now()
stock ="GBPUSD=X"
data = pdr.get_data_yahoo(stock, start_date, end_date)
df= data["Close"]
print(df)

# 하고싶은것
1. GBP 대비 USD, JPY, KOR, EURO % change를 그래프로 보여주자, plotly 사용 후 대시보드 만들기 (그래프 추가 빼기
가능하게 )