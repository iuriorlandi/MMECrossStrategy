import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import backtrader.feeds as btfeeds

class MMECrossStrategy(bt.Strategy):
    params = (
        ("fast", 9),
        ("mid", 50),
        ("slow", 20),
        ("risk_reward_1", 1),  l
        ("risk_reward_2", 2),  
    )

    def __init__(self):
        self.mme_fast = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.fast)
        self.mme_mid = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.mid)
        self.mme_slow = bt.indicators.ExponentialMovingAverage(self.data.close, period=self.params.slow)
        self.order = None

    def next(self):
        if not self.position:
            if self.mme_fast[0] > self.mme_mid[0] > self.mme_slow[0] and self.data.close[0] > self.mme_fast[0]:
                print(f"Compra em {self.data.datetime.date()} a {self.data.close[0]}")
                stop_distance = self.data.close[0] - self.mme_mid[0]
                self.target1 = self.data.close[0] + self.params.risk_reward_1 * stop_distance
                self.target2 = self.data.close[0] + self.params.risk_reward_2 * stop_distance
                self.order = self.buy()

        else:
            if self.data.close[0] < self.mme_mid[0]:  # Stop loss
                print(f"STOP em {self.data.datetime.date()} a {self.data.close[0]}")
                self.close()
            elif self.data.close[0] > self.target1 and not hasattr(self, 'target1_hit'):
                print(f"Venda em {self.data.datetime.date()} a {self.data.close[0]}")
                # Realizar a primeira saída parcial de 50%
                self.sell(size=self.position.size/2)
                self.target1_hit = True
            elif hasattr(self, 'target1_hit') and self.data.close[0] > self.target2:
                print(f"Venda em {self.data.datetime.date()} a {self.data.close[0]}")
                # Realizar a segunda saída parcial
                self.close()

data  = btfeeds.YahooFinanceCSVData(dataname='MSFT.csv')

cerebro = bt.Cerebro()
cerebro.addstrategy(MMECrossStrategy)
cerebro.adddata(data)
cerebro.broker.set_cash(10000)
cerebro.run()
cerebro.plot(style='candlestick', barup='green', bardown='red')
