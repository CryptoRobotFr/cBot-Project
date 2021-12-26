import ccxt
import pandas as pd
import json
import time
import pickle
import os

class DataEngine():

    def __init__(self, session=ccxt.binance(), path_to_data='../database/'):
        self._session = session
        self.exchange_name = str(self._session)
        self._session.load_markets()
        self.path_to_data = path_to_data

    def get_historical_from_api(self, symbol, timeframe, start_date, limit=1000):
        '''
        Use pagination to get OHLCV from api with no limit of number
        Works with binance, ftx, hitbtc, (?)
        Does not work for (?)

        # Attributes
        @param symbol string: pair symbol i.e BTC/USDT
        @param timeframe string: timeframe symbol i.e 1h
        @param start_date string: a date in specif format i.e 2017-01-01T00:00:00
        @param limit int: let 1000 in most of the cases

        @return df pandas_dataframe: a pandas dataframe OHLCV with date in index
        '''
        try:
            temp_data = self._session.fetch_ohlcv(symbol, timeframe, int(
                time.time()*1000)-1209600000, limit=limit)
            dtemp = pd.DataFrame(temp_data)
            temp_inter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
        except:
            return None

        finished = False
        start = False
        all_df = []
        start_date = self._session.parse8601(start_date)
        while(start == False):
            try:
                temp_data = self._session.fetch_ohlcv(
                    symbol, timeframe, start_date, limit=limit)
                dtemp = pd.DataFrame(temp_data)
                temp_inter = int(dtemp.iloc[-1][0] - dtemp.iloc[-2][0])
                next_time = int(dtemp.iloc[-1][0] + temp_inter)
                all_df.append(dtemp)
                start = True
            except:
                start_date = start_date + 1209600000*2

        if dtemp.shape[0] < 1:
            finished = True
        while(finished == False):
            try:
                temp_data = self._session.fetch_ohlcv(
                    symbol, timeframe, next_time, limit=limit)
                dtemp = pd.DataFrame(temp_data)
                next_time = int(dtemp.iloc[-1][0] + temp_inter)
                all_df.append(dtemp)
                # print(dtemp.iloc[-1][0])
                if dtemp.shape[0] < 1:
                    finished = True
            except:
                finished = True
        result = pd.concat(all_df, ignore_index=True, sort=False)
        result = result.rename(
            columns={0: 'timestamp', 1: 'open', 2: 'high', 3: 'low', 4: 'close', 5: 'volume'})
        result = result.set_index(result['timestamp'])
        result.index = pd.to_datetime(result.index, unit='ms')
        del result['timestamp']
        return result


    def get_historical_from_db(self, symbol, timeframe, start_date):
        '''
        Get the OHLCV from local pickle file
        Works for all exchange in database
        
        # Attributes
        @param symbol string: pair symbol i.e BTC/USDT
        @param timeframe string: timeframe symbol i.e 1h
        @param start_date string: a date in specif format i.e 2017-01-01T00:00:00

        @return df pandas_dataframe: a pandas dataframe OHLCV with date in index
        '''
        symbol = symbol.replace('/','')
        try:
            dbfile = open(self.path_to_data+self.exchange_name+'/'+timeframe+'/'+symbol+'.p', 'rb')	
            df = pickle.load(dbfile)
            dbfile.close()
            df = df.loc[start_date:]
            try:
                print("Successfully load",len(df),"candles for",symbol)
                return df
            except:
                print('!',self.path_to_data+self.exchange_name+'/'+timeframe+'/'+symbol+'.p'+' is empty')
                return None
        except:
            print(self.path_to_data+self.exchange_name+'/'+timeframe+'/'+symbol+'.p'+' not exist or error')
            return None

    def download_data(self, symbols, timeframes, start_date='2017-01-01T00:00:00'):
        '''
        Download in database for all timeframes for all symbols the OHLCV pandas dataframe since start date
        Work for same exchange as get_historical_from_api()

        # Attributes
        @param symbols string array: pair symbol i.e ["BTC/USDT","ETH/USDT"]
        @param timeframe string array: timeframe symbol i.e ["1d","1h"]
        @param start_date string: a date in specif format i.e 2017-01-01T00:00:00
        '''
        for symbol in symbols:
            for tf in timeframes:
                print(f'-> downloding symbol {symbol} for timeframe {tf}')
                df = self.get_historical_from_api(symbol=symbol, timeframe=tf, start_date=start_date)
                if df is not None and len(df) > 0:
                    try:
                        fileName = self.path_to_data+self.exchange_name+'/'+tf+'/'+symbol.replace('/','')+'.p'
                        if os.path.exists(fileName):
                            os.remove(fileName)
                        dbfile = open(fileName, 'ab')
                        pickle.dump(df, dbfile)					
                        dbfile.close()
                        print(symbol, len(df), "Candles", tf, "load since the :", df.index[0],'to :',df.index[-1], 'in', fileName)
                    except:
                        pass
                        print('Error on', symbol)
                else:
                    print('Error empty dataframe on', symbol)

    def update_data(self, symbols, timeframes):
        '''
        Take dataframe from db and update only data since the last one to now
        Work for binance, ftx, (?)
        Does not work for hitbtc, (?)

        # Attributes
        @param symbols string array: pair symbol i.e ["BTC/USDT","ETH/USDT"]
        @param timeframe string array: timeframe symbol i.e ["1d","1h"]
        @param start_date string: a date in specif format i.e 2017-01-01T00:00:00
        '''
        for symbol in symbols:
            for tf in timeframes:
                try:
                    fileName = self.path_to_data+self.exchange_name+'/'+tf+'/'+symbol.replace('/','')+'.p'
                    # -- Load Data --
                    with open(fileName, 'rb') as file:
                        dfOrigin = pickle.load(file)

                    start_date = dfOrigin.index[-1]
                    dfNew = self.get_historical_from_api(symbol, tf, start_date)
                    dfNew = dfNew.loc[start_date:].iloc[1:]
                    dfFinal = pd.concat([dfOrigin,dfNew])
                    if len(dfFinal) > 0:
                        with open(fileName, 'wb') as file:
                            pickle.dump(dfFinal, file)
                    print(symbol, len(dfNew), "New candles", tf, "load since the :", dfFinal.index[0], 'in', fileName)
                except:
                    print("Error on", symbol, tf)
