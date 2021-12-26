import sys
sys.path.append('cBot-Project/utilities')
from custom_indicators import CustomIndocators as ci
from spot_ftx import SpotFtx
import pandas as pd
import ta
import ccxt
from datetime import datetime
import time

now = datetime.now()
print(now.strftime("%d-%m %H:%M:%S"))

ftx = SpotFtx(
        apiKey='',
        secret='',
        subAccountName=''
    )

pairList = [
    'BTC/USD',
    'ETH/USD',
    'BNB/USD',
    'LTC/USD',
    'DOGE/USD',
    'XRP/USD',
    'SOL/USD',
    'AVAX/USD',
    'SHIB/USD',
    'LINK/USD',
    'UNI/USD',
    'MATIC/USD',
    'AXS/USD',
    'CRO/USD',
    'FTT/USD',
    'TRX/USD',
    'BCH/USD',
    'FTM/USD',
    'GRT/USD',
    'AAVE/USD',
    'OMG/USD',
    'SUSHI/USD',
    'MANA/USD',
    'SRM/USD',
    'RUNE/USD',
    'SAND/USD',
    'CHZ/USD',
    'CRV/USD'
]

timeframe = '1h'

# -- Indicator variable --
aoParam1 = 6
aoParam2 = 22
stochWindow = 14
willWindow = 14

# -- Hyper parameters --
maxOpenPosition = 3
stochOverBought = 0.8
stochOverSold = 0.2
willOverSold = -85
willOverBought = -10
TpPct = 0.15

dfList = {}
for pair in pairList:
    # print(pair)
    df = ftx.get_last_historical(pair, timeframe, 210)
    dfList[pair.replace('/USD','')] = df

for coin in dfList:
    # -- Drop all columns we do not need --
    dfList[coin].drop(columns=dfList[coin].columns.difference(['open','high','low','close','volume']), inplace=True)

    # -- Indicators, you can edit every value --
    dfList[coin]['AO']= ta.momentum.awesome_oscillator(dfList[coin]['high'],dfList[coin]['low'],window1=aoParam1,window2=aoParam2)
    dfList[coin]['STOCH_RSI'] = ta.momentum.stochrsi(close=dfList[coin]['close'], window=stochWindow)
    dfList[coin]['WillR'] = ta.momentum.williams_r(high=dfList[coin]['high'], low=dfList[coin]['low'], close=dfList[coin]['close'], lbp=willWindow)
    dfList[coin]['EMA100'] =ta.trend.ema_indicator(close=dfList[coin]['close'], window=100)
    dfList[coin]['EMA200'] =ta.trend.ema_indicator(close=dfList[coin]['close'], window=200)
        
print("Data and Indicators loaded 100%")

# -- Condition to BUY market --
def buyCondition(row, previousRow=None):
    if (
        row['AO'] >= 0
        and previousRow['AO'] > row['AO']
        and row['WillR'] < willOverSold
        and row['EMA100'] > row['EMA200']
    ):
        return True
    else:
        return False

# -- Condition to SELL market --
def sellCondition(row, previousRow=None):
    if (
        (row['AO'] < 0
        and row['STOCH_RSI'] > stochOverSold)
        or row['WillR'] > willOverBought
    ):
        return True
    else:
        return False
    
coinBalance = ftx.get_all_balance()
coinInUsd = ftx.get_all_balance_in_usd()
usdBalance = coinBalance['USD']
del coinBalance['USD']
del coinInUsd['USD']
totalBalanceInUsd = usdBalance + sum(coinInUsd.values())
coinPositionList = []
for coin in coinInUsd:
    if coinInUsd[coin] > 0.05 * totalBalanceInUsd:
        coinPositionList.append(coin)
openPositions = len(coinPositionList)

#Sell
for coin in coinPositionList:
        if sellCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True:
            openPositions -= 1
            symbol = coin+'/USD'
            cancel = ftx.cancel_all_open_order(symbol)
            time.sleep(1)
            sell = ftx.place_market_order(symbol,'sell',coinBalance[coin])
            print(cancel)
            print("Sell", coinBalance[coin], coin, sell)
        else:
            print("Keep",coin)

#Buy
if openPositions < maxOpenPosition:
    for coin in dfList:
        if coin not in coinPositionList:
            if buyCondition(dfList[coin].iloc[-2], dfList[coin].iloc[-3]) == True and openPositions < maxOpenPosition:
                time.sleep(1)
                usdBalance = ftx.get_balance_of_one_coin('USD')
                symbol = coin+'/USD'

                buyPrice = float(ftx.convert_price_to_precision(symbol, ftx.get_bid_ask_price(symbol)['ask'])) 
                tpPrice = float(ftx.convert_price_to_precision(symbol, buyPrice + TpPct * buyPrice))
                buyQuantityInUsd = usdBalance * 1/(maxOpenPosition-openPositions)

                if openPositions == maxOpenPosition - 1:
                    buyQuantityInUsd = 0.95 * buyQuantityInUsd

                buyAmount = ftx.convert_amount_to_precision(symbol, buyQuantityInUsd/buyPrice)

                buy = ftx.place_market_order(symbol,'buy',buyAmount)
                time.sleep(2)
                tp = ftx.place_limit_order(symbol,'sell',buyAmount,tpPrice)
                try:
                    tp["id"]
                except:
                    time.sleep(2)
                    tp = ftx.place_limit_order(symbol,'sell',buyAmount,tpPrice)
                    pass
                print("Buy",buyAmount,coin,'at',buyPrice,buy)
                print("Place",buyAmount,coin,"TP at",tpPrice, tp)

                openPositions += 1
