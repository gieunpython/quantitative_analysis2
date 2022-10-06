import datetime
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr
import backtrader as bt

# import data

def get_data(stocks, start, end):
    stockData = pdr.get_data_yahoo(stocks, start, end)
    return stockData

stockList = ['VTS.AX']
endDate = datetime.datetime.now()
startDate = endDate - datetime.timedelta(days=5000)

stockData = get_data(stockList[0], startDate, endDate)

actualStart = stockData.index[0]

data = bt.feeds.PandasData(dataname = stockData)

class BuyAndHold(bt.Strategy):
    def start(self):
        self.val_start = self.broker.get_cash()
    def nextstart(self):
        size = math.floor( (self.broker.get_cash() - 10) / self.data[0] )
        self.buy(size=size)
    def stop(self):
        # calculate actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1
        print('-'*50)
        print('BUY & HOLD')
        print('Starting Value:  ${:,.2f}'.format(self.val_start))
        print('ROI:              {:.2f}%'.format(self.roi * 100.0))
        print('Annualised:       {:.2f}%'.format(100*((1+self.roi)**(365/(endDate-actualStart).days) -1)))
        print('Gross Return:    ${:,.2f}'.format(self.broker.get_value() - self.val_start))

class BuyAndHold_More_Fund(bt.Strategy):
    params = dict(
        monthly_cash =1000,
        monthly_range = [5, 20]
    )

    def __init__(self):
        self.order = None
        self.totalcost = 0
        self.cost_wo_bro = 0
        self.units = 0
        self.times = 0
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' %(dt.isoformat(), txt))

    def start(self):
        self.broker.set_fundmode(fundmode=True, fundstartval=100.0)

        self.cash_start = self.broker.get_cash()
        self.val_start = 100.0

        #ADD A TIMER
        self.add_timer(
            when= bt.timer.SESSION_START,
            monthdays=[i for i in self.p.monthly_range],
            monthcarry=True
            #timername='buytimer'
        )

    def notify_timer(self, timer, when, *args):
        self.broker.add_cash(self.p.monthly_cash)

        target_value = self.broker.get_value() + self.p.monthly_cash - 10
        self.order_target_value(target=target_value)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return 
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price %.2f, Cost %.2f, Comm %.2f, Size %.0f' %
                    (order.executed.price,
                    order.executed.value,
                    order.executed.comm,
                    order.executed.size)
                )

                self.units += order.executed.size
                self.totalcost += order.executed.value
                self.cost_wo_bro += order.executed.value 
                self.times += 1
            
            elif order.status in [order.Canceled, order.Margin, order.Rejected]:
                self.log('Order Canceled/Margin/Rejected')
                print(order.status, [order.Canceled, order.Margin, order.Rejected])

                self.order = None

    def stop(self):
        # calculate actual returns
        self.roi= ((self.broker.get_value() / self.cash_start) - 1)
        self.froi = (self.broker.get_fundvalue() - self.val_start)
        value = self.datas[0].close * self.units + self.broker.get_cash()
        print('-'*50)
        print('BUY & BUY MORE')
        print('Time in Market: {:.1f} years'.format((endDate - actualStart).days/365))
        print('#Times:         {:.0f}'.format(self.times))
        print('Value:         ${:,.2f}'.format(value))
        print('Cost:          ${:,.2f}'.format(self.totalcost))
        print('Gross Return:  ${:,.2f}'.format(value - self.totalcost))
        print('Gross %:        {:.2f}%'.format((value/self.totalcost - 1) * 100))
        print('ROI:            {:.2f}%'.format(100.0 * self.roi))
        print('Fund Value:     {:.2f}%'.format(self.froi))
        print('Annualised:     {:.2f}%'.format(100*((1+self.froi/100)**(365/(endDate - actualStart).days) - 1)))
        print('-'*50)

class FixedCommisionScheme(bt.CommInfoBase):
    paras = (
        ('commission', 10),
        ('stocklike', True),
        ('commtype', bt.CommInfoBase.COMM_FIXED)

    )

    def _getcommission(self, size, price, pseudoexec):
        return self.p.commission

def run(data):
    # BUY AND HOLD 
    cerebro =bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(BuyAndHold)

    #Broker Information
    broker_args = dict(coc=True)
    cerebro.broker = bt.brokers.BackBroker(**broker_args)
    comminfo = FixedCommisionScheme()
    cerebro.broker.addcommissioninfo(comminfo)

    cerebro.broker.set_cash(100000)

    
    # BUY AND BUY MORE 
    cerebro1 =bt.Cerebro()
    cerebro1.adddata(data)
    cerebro1.addstrategy(BuyAndHold_More_Fund)

    #Broker Information
    broker_args = dict(coc=True)
    cerebro1.broker = bt.brokers.BackBroker(**broker_args)
    comminfo = FixedCommisionScheme()
    cerebro1.broker.addcommissioninfo(comminfo)

    cerebro1.broker.set_cash(1000)

    cerebro1.run()
    cerebro.run()
    cerebro.plot(iplot=False, style='candlestick')
    cerebro1.plot(iplot=False, style='candlestick')

if __name__ == '__main__':
    run(data)