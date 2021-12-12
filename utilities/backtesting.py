import pandas as pd
import math
from datetime import datetime
import matplotlib.pyplot as plt
import random
import numpy as np
import seaborn as sns
import datetime

class Backtesting():

    def simple_spot_backtest_analys(self, dfTrades, dfTest, pairSymbol, timeframe):
        # -- BackTest Analyses --
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()*100
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat'] = None
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat%'] = None

        dfTrades['tradeIs'] = ''
        dfTrades.loc[dfTrades['resultat'] > 0, 'tradeIs'] = 'Good'
        dfTrades.loc[dfTrades['resultat'] <= 0, 'tradeIs'] = 'Bad'

        dfTrades['walletAth'] = dfTrades['wallet'].cummax()
        dfTrades['drawDown'] = dfTrades['walletAth'] - dfTrades['wallet']
        dfTrades['drawDownPct'] = dfTrades['drawDown'] / dfTrades['walletAth']

        wallet = dfTrades.iloc[-1]['wallet']
        iniClose = dfTest.iloc[0]['close']
        lastClose = dfTest.iloc[len(dfTest)-1]['close']
        holdPercentage = ((lastClose - iniClose)/iniClose) * 100
        initalWallet = dfTrades.iloc[0]['wallet']
        algoPercentage = ((wallet - initalWallet)/initalWallet) * 100
        holdFinalWallet = initalWallet + initalWallet*(holdPercentage/100)
        vsHoldPercentage = ((wallet/holdFinalWallet)-1)*100

        try:
            tradesPerformance = round(dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                      / dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
        except:
            tradesPerformance = 0
            print(
                "/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")

        try:
            totalGoodTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Good'])
            AveragePercentagePositivTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].sum()
                                                    / totalGoodTrades, 2)
            idbest = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Good', 'resultat%'].idxmax()
            bestTrade = str(
                round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].max(), 2))
        except:
            totalGoodTrades = 0
            AveragePercentagePositivTrades = 0
            idbest = ''
            bestTrade = 0
            print("/!\ There is no Good Trades in your BackTest, maybe a problem...")

        try:
            totalBadTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Bad'])
            AveragePercentageNegativTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].sum()
                                                    / totalBadTrades, 2)
            idworst = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Bad', 'resultat%'].idxmin()
            worstTrade = round(
                dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
        except:
            totalBadTrades = 0
            AveragePercentageNegativTrades = 0
            idworst = ''
            worstTrade = 0
            print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")

        totalTrades = totalBadTrades + totalGoodTrades
        winRateRatio = (totalGoodTrades/totalTrades) * 100

        try:
            dfTrades['timeDeltaTrade'] = dfTrades["timeSince"]
            dfTrades['timeDeltaNoTrade'] = dfTrades['timeDeltaTrade']
            dfTrades.loc[dfTrades['position'] ==
                         'Buy', 'timeDeltaTrade'] = None
            dfTrades.loc[dfTrades['position'] ==
                         'Sell', 'timeDeltaNoTrade'] = None
        except:
            print("/!\ Error in time delta")
            dfTrades['timeDeltaTrade'] = 0
            dfTrades['timeDeltaNoTrade'] = 0

        reasons = dfTrades['reason'].unique()

        print("Pair Symbol :", pairSymbol, '| Timeframe :', timeframe)
        print("Period : [" + str(dfTest.index[0]) + "] -> [" +
              str(dfTest.index[len(dfTest)-1]) + "]")
        print("Starting balance :", initalWallet, "$")

        print("\n----- General Informations -----")
        print("Final balance :", round(wallet, 2), "$")
        print("Performance vs US Dollar :", round(algoPercentage, 2), "%")
        print("Buy and Hold Performence :", round(holdPercentage, 2), "%")
        print("Performance vs Buy and Hold :", round(vsHoldPercentage, 2), "%")
        print("Best trade : +"+bestTrade, "%, the", idbest)
        print("Worst trade :", worstTrade, "%, the", idworst)
        print("Worst drawDown : -", str(
            round(100*dfTrades['drawDownPct'].max(), 2)), "%")
        print("Total fees : ", round(dfTrades['frais'].sum(), 2), "$")

        print("\n----- Trades Informations -----")
        print("Total trades on period :", totalTrades)
        print("Number of positive trades :", totalGoodTrades)
        print("Number of negative trades : ", totalBadTrades)
        print("Trades win rate ratio :", round(winRateRatio, 2), '%')
        print("Average trades performance :", tradesPerformance, "%")
        print("Average positive trades :", AveragePercentagePositivTrades, "%")
        print("Average negative trades :", AveragePercentageNegativTrades, "%")

        print("\n----- Time Informations -----")
        print("Average time duration for a trade :", round(
            dfTrades['timeDeltaTrade'].mean(skipna=True), 2), "periods")
        print("Maximum time duration for a trade :",
              dfTrades['timeDeltaTrade'].max(skipna=True), "periods")
        print("Minimum time duration for a trade :",
              dfTrades['timeDeltaTrade'].min(skipna=True), "periods")
        print("Average time duration between two trades :", round(
            dfTrades['timeDeltaNoTrade'].mean(skipna=True), 2), "periods")
        print("Maximum time duration between two trades :",
              dfTrades['timeDeltaNoTrade'].max(skipna=True), "periods")
        print("Minimum time duration between two trades :",
              dfTrades['timeDeltaNoTrade'].min(skipna=True), "periods")

        print("\n----- Trades Reasons -----")
        reasons = dfTrades['reason'].unique()
        for r in reasons:
            print(r+" number :", dfTrades.groupby('reason')
                  ['date'].nunique()[r])

        return dfTrades

    def multi_spot_backtest_analys(self, dfTrades, dfTest, pairList, timeframe):
        # -- BackTest Analyses --
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()*100
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat'] = None
        dfTrades.loc[dfTrades['position'] == 'Buy', 'resultat%'] = None

        dfTrades['tradeIs'] = ''
        dfTrades.loc[dfTrades['resultat'] > 0, 'tradeIs'] = 'Good'
        dfTrades.loc[dfTrades['resultat'] <= 0, 'tradeIs'] = 'Bad'

        dfTrades['walletAth'] = dfTrades['wallet'].cummax()
        dfTrades['drawDown'] = dfTrades['walletAth'] - dfTrades['wallet']
        dfTrades['drawDownPct'] = dfTrades['drawDown'] / dfTrades['walletAth']

        wallet = dfTrades.iloc[-1]['wallet']
        iniClose = dfTest.iloc[0]['close']
        lastClose = dfTest.iloc[len(dfTest)-1]['close']
        holdPercentage = ((lastClose - iniClose)/iniClose) * 100
        initalWallet = dfTrades.iloc[0]['wallet']
        algoPercentage = ((wallet - initalWallet)/initalWallet) * 100
        holdFinalWallet = initalWallet + initalWallet*(holdPercentage/100)
        vsHoldPercentage = ((wallet/holdFinalWallet)-1)*100

        try:
            tradesPerformance = round(dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].sum()
                                        / dfTrades.loc[(dfTrades['tradeIs'] == 'Good') | (dfTrades['tradeIs'] == 'Bad'), 'resultat%'].count(), 2)
        except:
            tradesPerformance = 0
            print(
                "/!\ There is no Good or Bad Trades in your BackTest, maybe a problem...")

        try:
            totalGoodTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Good'])
            AveragePercentagePositivTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].sum()
                                                    / totalGoodTrades, 2)
            idbest = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Good', 'resultat%'].idxmax()
            bestTrade = str(
                round(dfTrades.loc[dfTrades['tradeIs'] == 'Good', 'resultat%'].max(), 2))
        except:
            totalGoodTrades = 0
            AveragePercentagePositivTrades = 0
            idbest = ''
            bestTrade = 0
            print("/!\ There is no Good Trades in your BackTest, maybe a problem...")

        try:
            totalBadTrades = len(dfTrades.loc[dfTrades['tradeIs'] == 'Bad'])
            AveragePercentageNegativTrades = round(dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].sum()
                                                    / totalBadTrades, 2)
            idworst = dfTrades.loc[dfTrades['tradeIs']
                                    == 'Bad', 'resultat%'].idxmin()
            worstTrade = round(
                dfTrades.loc[dfTrades['tradeIs'] == 'Bad', 'resultat%'].min(), 2)
        except:
            totalBadTrades = 0
            AveragePercentageNegativTrades = 0
            idworst = ''
            worstTrade = 0
            print("/!\ There is no Bad Trades in your BackTest, maybe a problem...")

        totalTrades = totalBadTrades + totalGoodTrades
        winRateRatio = (totalGoodTrades/totalTrades) * 100


        print("Trading Bot on :", len(pairList), 'coins | Timeframe :', timeframe)
        print("Period : [" + str(dfTest.index[0]) + "] -> [" +
                str(dfTest.index[len(dfTest)-1]) + "]")
        print("Starting balance :", initalWallet, "$")

        print("\n----- General Informations -----")
        print("Final balance :", round(wallet, 2), "$")
        print("Performance vs US Dollar :", round(algoPercentage, 2), "%")
        print("Bitcoin Buy and Hold Performence :", round(holdPercentage, 2), "%")
        print("Performance vs Buy and Hold :", round(vsHoldPercentage, 2), "%")
        print("Best trade : +"+bestTrade, "%, the", idbest)
        print("Worst trade :", worstTrade, "%, the", idworst)
        print("Worst drawDown : -", str(
            round(100*dfTrades['drawDownPct'].max(), 2)), "%")
        print("Total fees : ", round(dfTrades['frais'].sum(), 2), "$")

        print("\n----- Trades Informations -----")
        print("Total trades on period :", totalTrades)
        print("Number of positive trades :", totalGoodTrades)
        print("Number of negative trades : ", totalBadTrades)
        print("Trades win rate ratio :", round(winRateRatio, 2), '%')
        print("Average trades performance :", tradesPerformance, "%")
        print("Average positive trades :", AveragePercentagePositivTrades, "%")
        print("Average negative trades :", AveragePercentageNegativTrades, "%")

        print("\n----- Trades Reasons -----")
        print(dfTrades['reason'].value_counts())

        print("\n----- Pair Result -----")
        dash = '-' * 95
        print(dash)
        print('{:<6s}{:>10s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}'.format(
            "Trades","Pair","Sum-result","Mean-trade","Worst-trade","Best-trade","Win-rate"
            ))
        print(dash)
        for pair in pairList:
            try:
                dfPairLoc = dfTrades.loc[dfTrades['symbol'] == pair, 'resultat%']
                pairGoodTrade = len(dfTrades.loc[(dfTrades['symbol'] == pair) & (dfTrades['resultat%'] > 0)])
                pairTotalTrade = int(len(dfPairLoc)/2)
                pairResult = str(round(dfPairLoc.sum(),2))+' %'
                pairAverage = str(round(dfPairLoc.mean(),2))+' %'
                pairMin = str(round(dfPairLoc.min(),2))+' %'
                pairMax = str(round(dfPairLoc.max(),2))+' %'
                pairWinRate = str(round(100*(pairGoodTrade/pairTotalTrade),2))+' %'
                print('{:<6d}{:>10s}{:>15s}{:>15s}{:>15s}{:>15s}{:>15s}'.format(
                    pairTotalTrade,pair,pairResult,pairAverage,pairMin,pairMax,pairWinRate
                ))
            except:
                pass

        return dfTrades

    def get_result_by_month(self, dfTrades):
        lastMonth = int(dfTrades.iloc[-1]['date'].month)
        lastYear = int(dfTrades.iloc[-1]['date'].year)
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        myMonth = int(dfTrades.iloc[0]['date'].month)
        myYear = int(dfTrades.iloc[0]['date'].year)
        while myYear != lastYear or myMonth != lastMonth:
            myString = str(myYear) + "-" + str(myMonth)
            try:
                myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                            dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
            except:
                myResult = 0
            print(myYear, myMonth, round(myResult*100, 2), "%")
            if myMonth < 12:
                myMonth += 1
            else:
                myMonth = 1
                myYear += 1

        myString = str(lastYear) + "-" + str(lastMonth)
        try:
            myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                        dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
        except:
            myResult = 0
        print(lastYear, lastMonth, round(myResult*100, 2), "%")

    def plot_wallet_vs_price(self, dfTrades):
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades[['wallet', 'price']].plot(subplots=True, figsize=(20, 10))
        print("\n----- Plot -----")

    def plot_wallet_evolution(self, dfTrades):
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['wallet'].plot(figsize=(20, 10))
        print("\n----- Plot -----")

    def plot_bar_by_month(self, dfTrades):
        sns.set(rc={'figure.figsize':(11.7,8.27)})
        lastMonth = int(dfTrades.iloc[-1]['date'].month)
        lastYear = int(dfTrades.iloc[-1]['date'].year)
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        myMonth = int(dfTrades.iloc[0]['date'].month)
        myYear = int(dfTrades.iloc[0]['date'].year)
        custom_palette = {}
        dfTemp = pd.DataFrame([])
        while myYear != lastYear or myMonth != lastMonth:
            myString = str(myYear) + "-" + str(myMonth)
            try:
                myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                            dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
            except:
                myResult = 0
            myrow = {
                'date': str(datetime.date(1900, myMonth, 1).strftime('%B')),
                'result': round(myResult*100)
            }
            dfTemp = dfTemp.append(myrow, ignore_index=True)
            if myResult >= 0:
                custom_palette[str(datetime.date(1900, myMonth, 1).strftime('%B'))] = 'g'
            else:
                custom_palette[str(datetime.date(1900, myMonth, 1).strftime('%B'))] = 'r'
            # print(myYear, myMonth, round(myResult*100, 2), "%")
            if myMonth < 12:
                myMonth += 1
            else:
                g = sns.barplot(data=dfTemp,x='date',y='result', palette=custom_palette)
                for index, row in dfTemp.iterrows():
                    if row.result >= 0:
                        g.text(row.name,row.result, '+'+str(round(row.result))+'%', color='black', ha="center", va="bottom")
                    else:
                        g.text(row.name,row.result, '-'+str(round(row.result))+'%', color='black', ha="center", va="top")
                g.set_title(str(myYear) + ' performance in %')
                g.set(xlabel=myYear, ylabel='performance %')
                yearResult = (dfTrades.loc[str(myYear)].iloc[-1]['wallet'] -
                            dfTrades.loc[str(myYear)].iloc[0]['wallet'])/dfTrades.loc[str(myYear)].iloc[0]['wallet']
                print("----- " + str(myYear) +" Performances: " + str(round(yearResult*100,2)) + "% -----")
                plt.show()
                dfTemp = pd.DataFrame([])
                myMonth = 1
                myYear += 1

        myString = str(lastYear) + "-" + str(lastMonth)
        try:
            myResult = (dfTrades.loc[myString].iloc[-1]['wallet'] -
                        dfTrades.loc[myString].iloc[0]['wallet'])/dfTrades.loc[myString].iloc[0]['wallet']
        except:
            myResult = 0
        g = sns.barplot(data=dfTemp,x='date',y='result', palette=custom_palette)
        for index, row in dfTemp.iterrows():
            if row.result >= 0:
                g.text(row.name,row.result, '+'+str(round(row.result))+'%', color='black', ha="center", va="bottom")
            else:
                g.text(row.name,row.result, '-'+str(round(row.result))+'%', color='black', ha="center", va="top")
        g.set_title(str(myYear) + ' performance in %')
        g.set(xlabel=myYear, ylabel='performance %')
        yearResult = (dfTrades.loc[str(myYear)].iloc[-1]['wallet'] -
                dfTrades.loc[str(myYear)].iloc[0]['wallet'])/dfTrades.loc[str(myYear)].iloc[0]['wallet']
        print("----- " + str(myYear) +" Performances: " + str(round(yearResult*100,2)) + "% -----")
        plt.show()

    def past_simulation(
            self, 
            dfTrades, 
            numberOfSimulation = 100,
            lastTrainDate = "2021-06",
            firstPlottedDate = "2021-07",
            firstSimulationDate = "2021-07-15",
            trainMultiplier = 1
        ):
        dfTrades = dfTrades.set_index(dfTrades['date'])
        dfTrades.index = pd.to_datetime(dfTrades.index)
        dfTrades['resultat'] = dfTrades['wallet'].diff()
        dfTrades['resultat%'] = dfTrades['wallet'].pct_change()
        dfTrades = dfTrades.loc[dfTrades['position']=='Sell','resultat%']
        dfTrades = dfTrades + 1

        suimulationResult = []
        trainSeries = dfTrades.loc[:lastTrainDate]
        startedPlottedDate = firstPlottedDate
        startedSimulationDate = firstSimulationDate
        commonPlot = dfTrades.copy().loc[startedPlottedDate:startedSimulationDate]
        simulatedTradesLength = len(dfTrades.loc[startedSimulationDate:])
        for i in range(numberOfSimulation):
            dfTemp = dfTrades.copy().loc[startedPlottedDate:]
            newTrades = random.sample(list(trainSeries)*trainMultiplier, simulatedTradesLength)
            dfTemp.iloc[-simulatedTradesLength:] = newTrades
            dfTemp = dfTemp.cumprod()
            dfTemp.plot(figsize=(20, 10))
            suimulationResult.append(dfTemp.iloc[-1])

        dfTemp = dfTrades.copy().loc[startedPlottedDate:]
        dfTemp = dfTemp.cumprod()
        dfTemp.plot(figsize=(20, 10), linewidth=8)
        trueResult = dfTemp.iloc[-1]
        suimulationResult.append(trueResult)
        suimulationResult.sort()
        resultPosition = suimulationResult.index(trueResult)
        resultPlacePct = round((resultPosition/len(suimulationResult))*100,2)
        maxSimulationResult = round((max(suimulationResult)-1)*100,2)
        minSimulationResult = round((min(suimulationResult)-1)*100,2)
        avgSimulationResult = round(((sum(suimulationResult)/len(suimulationResult))-1)*100,2)
        initialStrategyResult = round((trueResult-1)*100,2)

        print("Train data informations :",len(trainSeries),"trades on period [" + str(trainSeries.index[0]) + "] -> [" +
              str(trainSeries.index[len(trainSeries)-1]) + "]")
        print("The strategy is placed at",resultPlacePct,"% of all simulations")
        print("You strategy make +",initialStrategyResult,"%")
        print("The average simulation was at +",avgSimulationResult,"%")
        print("The best simulation was at +",maxSimulationResult,"%")
        print("The worst simulation was at +",minSimulationResult,"%")
        print("--- PLOT ---")        