#-*- coding: utf-8 -*-
import json
import requests
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore", message="guid format is not registered with bravado-core!")

class chart_bitfinex:
    def __init__(self, periods='1m', count=300):
        self.lowvalue = 0.00001
        self.data = self.getdata(periods, count)
        self.mfi = []
        self.mfi.append(self.getmfi(count=14, start=0))
        self.cmf = []
        self.cmf.append(self.getcmf(count=20, start=0))
        self.stochastic = []
        self.stochastic.append(self.getstochastic(count=14, start=0))
        self.stochastic_sma = []
        self.stochastic_sma.append(self.getstochastic_sma(count=14, start=0, arg_d=3))

    def getdata(self, periods, count):  # 환율
        # getdata('1m', 30)
        # https://api.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist?limit=10
        url = 'https://api.bitfinex.com/v2/candles/trade:' + str(periods) + ':tBTCUSD/hist?limit=' + str(count)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        tmp = json.loads(str(requests.get(url, headers=headers).text.strip()))
        result = []
        for i in range(len(tmp)):
            result.append({'mts': tmp[i][0], 'open': tmp[i][1], 'close': tmp[i][2], 'high': tmp[i][3], 'low': tmp[i][4],
                           'volume': tmp[i][5]})
        self.data = result
        self.mfi = []
        self.cmf = []
        for i in range(10):
            self.mfi.append(self.getmfi(count = 14, start = i))
            self.mfi.append(self.getcmf(count = 20, start = i))
        return result

    def printdata(self):
        # x = np.linspace(0, 3*np.pi, 500)
        x = range(len(self.data))
        y = [self.data[i]['open'] for i in reversed(range(len(self.data)))]
        plt.plot(x, y)
        plt.title('data_show')
        plt.show()

    def getmfi(self, count=14, start=0):
        typical_price = []
        money_flow = {'positive': 0.0, 'negative': 0.0}
        for i in range(start, count + 1 + start):
            tmp = (self.data[i]['high'] + self.data[i]['low'] + self.data[i]['close']) / 3
            typical_price.append(tmp)
        j = 0
        for i in range(start, count + start):
            if typical_price[j] > typical_price[j + 1]:
                money_flow.update({'positive': money_flow['positive'] + (typical_price[j] * self.data[i]['volume'])})
            elif typical_price[j] < typical_price[j + 1]:
                money_flow.update({'negative': money_flow['negative'] + (typical_price[j] * self.data[i]['volume'])})
            j += 1
        try:
            ratio = money_flow['positive'] / money_flow['negative']
        except ZeroDivisionError:
            ratio = money_flow['positive'] / self.lowvalue
        except:
            return 'Error'
        result = 100 - (100 / (1 + ratio))
        return result

    def printmfi(self, count=14):
        self.mfi = []
        for i in range(len(self.data)):
            try:
                self.mfi.append(self.getmfi(count=count, start=i))
            except:
                break
        x = range(len(self.mfi))
        y = [self.mfi[i] for i in reversed(range(len(self.mfi)))]
        plt.plot(x, y)
        plt.title('mfi_show')
        plt.show()

    def getcmf(self, count=20, start=0):
        sum_volume = 0
        sum_money_flow_volume = 0
        for i in range(start, count + start):
            sum_volume += self.data[i]['volume']
        for i in range(start, count + start):
            try:
                money_flow_multiplier = ((self.data[i]['close'] - self.data[i]['low']) - (
                            self.data[i]['high'] - self.data[i]['close'])) / (
                                                    self.data[i]['high'] - self.data[i]['low'])
            except ZeroDivisionError:
                money_flow_multiplier = ((self.data[i]['close'] - self.data[i]['low']) - (
                            self.data[i]['high'] - self.data[i]['close'])) / self.lowvalue
            except:
                return 'Error'
            sum_money_flow_volume += money_flow_multiplier * self.data[i]['volume']
        try:
            cmf = sum_money_flow_volume / sum_volume
        except ZeroDivisionError:
            cmf = sum_money_flow_volume / self.lowvalue
        except:
            return 'Error'
        return cmf

    def printcmf(self, count=20):
        self.cmf = []
        for i in range(len(self.data)):
            try:
                self.cmf.append(self.getcmf(count=count, start=i))
            except:
                break
        x = range(len(self.cmf))
        y = [self.cmf[i] for i in reversed(range(len(self.cmf)))]
        plt.plot(x, y)
        plt.title('cmf_show')
        plt.show()

    def getstochastic(self, count=14, start=0):
        # k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        highest_high = self.data[start]['high']
        lowest_low = self.data[start]['low']
        current_close = self.data[start]['close']
        for i in range(start, count + start):
            if highest_high < self.data[i]['high']:
                highest_high = self.data[i]['high']
            if self.data[i]['low'] < lowest_low:
                lowest_low = self.data[i]['low']
        try:
            k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
        except ZeroDivisionError:
            k = ((current_close - lowest_low) / self.lowvalue) * 100
        except:
            return 'Error'
        return k

    def getstochastic_sma(self, count=14, start=0, arg_d=3):
        stochastic_sum = 0
        for i in range(arg_d):
            stochastic_sum += self.getstochastic(count=count, start=start + i)
        d = stochastic_sum / arg_d
        return d

    def printstochastic(self, count=14, arg_d=3):
        self.stochastic = []
        self.stochastic_sma = []
        for i in range(len(self.data)):
            try:
                self.stochastic.append(self.getstochastic(count=count, start=i))
                self.stochastic_sma.append(self.getstochastic_sma(count=count, start=i, arg_d=arg_d))
            except:
                break
        x = range(len(self.stochastic))
        y = [self.stochastic[i] for i in reversed(range(len(self.stochastic)))]
        plt.plot(x, y)
        plt.title('stochastic_show')
        plt.show()
        x = range(len(self.stochastic_sma))
        y = [self.stochastic_sma[i] for i in reversed(range(len(self.stochastic_sma)))]
        plt.plot(x, y)
        plt.title('stochastic_sma_show')
        plt.show()
