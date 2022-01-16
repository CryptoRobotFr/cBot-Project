import math
import numpy as np
import pandas as pd
import ta

class CustomIndocators():

    class trix():
        """ Trix indicator

            Args:
                close(pd.Series): dataframe 'close' columns,
                trixLength(int): the window length for each mooving average of the trix,
                trixSignal(int): the window length for the signal line
        """

        def __init__(
            self,
            close: pd.Series,
            trixLength: int = 9,
            trixSignal: int = 21
        ):
            self.close = close
            self.trixLength = trixLength
            self.trixSignal = trixSignal
            self._run()

        def _run(self):
            self.trixLine = ta.trend.ema_indicator(
                ta.trend.ema_indicator(
                    ta.trend.ema_indicator(
                        close=self.close, window=self.trixLength),
                    window=self.trixLength), window=self.trixLength)
            self.trixPctLine = self.trixLine.pct_change()*100
            self.trixSignalLine = ta.trend.sma_indicator(
                close=self.trixPctLine, window=self.trixSignal)
            self.trixHisto = self.trixPctLine - self.trixSignalLine

        def trix_line(self):
            """ trix line

                Returns:
                    pd.Series: trix line
            """
            return pd.Series(self.trixLine, name="TRIX_LINE")

        def trix_pct_line(self):
            """ trix percentage line

                Returns:
                    pd.Series: trix percentage line
            """
            return pd.Series(self.trixPctLine, name="TRIX_PCT_LINE")

        def trix_signal_line(self):
            """ trix signal line

                Returns:
                    pd.Series: trix siganl line
            """
            return pd.Series(self.trixSignal, name="TRIX_SIGNAL_LINE")

        def trix_histo(self):
            """ trix histogram

                Returns:
                    pd.Series: trix histogram
            """
            return pd.Series(self.trixHisto, name="TRIX_HISTO")

    def chop(high, low, close, window=14):
        """ Chopiness index

            Args:
                high(pd.Series): dataframe 'high' columns,
                low(pd.Series): dataframe 'low' columns,
                close(pd.Series): dataframe 'close' columns,
                window(int): the window length for the chopiness index,
            Returns:
                pd.Series: Chopiness index
        """
        tr1 = pd.DataFrame(high - low).rename(columns = {0:'tr1'})
        tr2 = pd.DataFrame(abs(high - close.shift(1))).rename(columns = {0:'tr2'})
        tr3 = pd.DataFrame(abs(low - close.shift(1))).rename(columns = {0:'tr3'})
        frames = [tr1, tr2, tr3]
        tr = pd.concat(frames, axis = 1, join = 'inner').dropna().max(axis = 1)
        atr = tr.rolling(1).mean()
        highh = high.rolling(window).max()
        lowl = low.rolling(window).min()
        chop = 100 * np.log10((atr.rolling(window).sum()) / (highh - lowl)) / np.log10(window)
        return pd.Series(chop, name="CHOP")

    def heikinAshiDf(df):
        """ HeikinAshi candles

            Args:
                df(pd.Dataframe): dataframe with 'open'|'high'|'low'|'close' columns
            Returns:
                pd.Dataframe: dataframe with 'HA_Open'|'HA_High'|'HA_Low'|'HA_Close' columns
        """
        df['HA_Close']=(df.open + df.high + df.low + df.close)/4
        ha_open = [ (df.open[0] + df.close[0]) / 2 ]
        [ ha_open.append((ha_open[i] + df.HA_Close.values[i]) / 2) \
        for i in range(0, len(df)-1) ]
        df['HA_Open'] = ha_open
        df['HA_High']=df[['HA_Open','HA_Close','high']].max(axis=1)
        df['HA_Low']=df[['HA_Open','HA_Close','low']].min(axis=1)
        return df

    def volume_anomality(df, volume_window=10):
        dfInd = df.copy()
        dfInd["VolAnomaly"] = 0
        dfInd["PreviousClose"] = dfInd["close"].shift(1)
        dfInd['MeanVolume'] = dfInd['volume'].rolling(volume_window).mean()
        dfInd['MaxVolume'] = dfInd['volume'].rolling(volume_window).max()
        dfInd.loc[dfInd['volume'] > 1.5 * dfInd['MeanVolume'], "VolAnomaly"] = 1
        dfInd.loc[dfInd['volume'] > 2 * dfInd['MeanVolume'], "VolAnomaly"] = 2
        dfInd.loc[dfInd['volume'] >= dfInd['MaxVolume'], "VolAnomaly"] = 3
        dfInd.loc[dfInd['PreviousClose'] > dfInd['close'],
                "VolAnomaly"] = (-1) * dfInd["VolAnomaly"]
        return dfInd["VolAnomaly"]