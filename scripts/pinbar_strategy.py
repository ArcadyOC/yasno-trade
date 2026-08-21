from datetime import timedelta

import pandas as pd
from base_strategy import BaseStrategy


class PinbarSweepStrategy(BaseStrategy):
    def __init__(self):
        self.name = "Liquidity Sweep v4 (без лонга в бычьем H1)"
        self.atr_period = 14
        self.sl_atr_buffer = 0.2
        self.min_risk_atr = 0.3
        self.skipped_h1_bull = 0
        self._atr_values = None
        self._atr_df_id = None
        self.h1 = None

    def set_hourly_context(self, h1_df: pd.DataFrame):
        """Часовые свечи для режима рынка. Без заглядывания в незакрытый час."""
        h1 = h1_df.copy()
        prev_close = h1["close"].shift(1)
        tr = pd.concat(
            [
                h1["high"] - h1["low"],
                (h1["high"] - prev_close).abs(),
                (h1["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        h1["sma20"] = h1["close"].rolling(20).mean()
        h1["sma20_prev"] = h1["sma20"].shift(5)
        h1["atr"] = tr.rolling(14).mean()
        h1["h1_close_time"] = h1.index + timedelta(hours=1)
        self.h1 = h1

    def _atr_series(self, df):
        if self._atr_df_id is id(df) and self._atr_values is not None:
            return self._atr_values
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        self._atr_values = tr.rolling(self.atr_period).mean()
        self._atr_df_id = id(df)
        return self._atr_values

    def _atr(self, df, current_index):
        return self._atr_series(df).iloc[current_index]

    def _h1_is_bull(self, m15_open) -> bool:
        if self.h1 is None:
            return False
        signal_close = m15_open + timedelta(minutes=15)
        usable = self.h1[self.h1["h1_close_time"] <= signal_close]
        if usable.empty:
            return False
        row = usable.iloc[-1]
        sma20, prev, close, atr = row["sma20"], row["sma20_prev"], row["close"], row["atr"]
        if pd.isna(sma20) or pd.isna(prev) or pd.isna(atr) or atr <= 0:
            return False
        slope = sma20 - prev
        if abs(slope) < 0.25 * atr:
            return False
        return close > sma20 and slope > 0

    def check_setup(self, df, current_index):
        """
        Лонг только если:
        1) нижняя тень > 60% диапазона;
        2) закрытие в верхней трети свечи;
        3) свеча не обновила 10-барный лой;
        4) стоп ниже low на 0.2 ATR, риск не меньше 0.3 ATR;
        5) последний закрытый H1 не в бычьем тренде.
        """
        if current_index < self.atr_period:
            return None

        current_candle = df.iloc[current_index]
        candle_range = current_candle["high"] - current_candle["low"]
        if candle_range <= 0.01:
            return None

        body_bottom = min(current_candle["open"], current_candle["close"])
        lower_wick = body_bottom - current_candle["low"]
        if (lower_wick / candle_range) <= 0.60:
            return None

        if current_candle["close"] < current_candle["low"] + candle_range * (2 / 3):
            return None

        prior_low = df["low"].iloc[current_index - 10 : current_index].min()
        if current_candle["low"] < prior_low:
            return None

        atr = self._atr(df, current_index)
        if pd.isna(atr) or atr <= 0:
            return None

        entry_price = current_candle["close"]
        sl_price = current_candle["low"] - self.sl_atr_buffer * atr
        risk_dist = entry_price - sl_price
        if risk_dist < self.min_risk_atr * atr:
            return None

        if self._h1_is_bull(df.index[current_index]):
            self.skipped_h1_bull += 1
            return None

        return {
            "entry_price": entry_price,
            "sl_price": sl_price,
            "direction": "long",
        }
