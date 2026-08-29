from datetime import timedelta

import pandas as pd
from base_strategy import BaseStrategy


class TrendPullbackStrategy(BaseStrategy):
    """Быстрая средняя развернулась по ходу старших часов, цена откатила к ней и оттолкнулась."""

    def __init__(self):
        self.name = "Trend Pullback"
        self.fast_period = 8
        self.slow_period = 21
        self.atr_period = 14
        self.sl_atr_buffer = 0.3
        self.min_risk_atr = 0.3
        self.bar_minutes = 15
        self.h1 = None
        self._cache_id = None
        self._fast = None
        self._slow = None
        self._atr = None

    def set_hourly_context(self, h1_df: pd.DataFrame):
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

    def _h1_is_bull(self, signal_time) -> bool:
        if self.h1 is None:
            return False
        usable = self.h1[self.h1["h1_close_time"] <= signal_time]
        if usable.empty:
            return False
        row = usable.iloc[-1]
        sma20, prev, close, atr = row["sma20"], row["sma20_prev"], row["close"], row["atr"]
        if pd.isna(sma20) or pd.isna(prev) or pd.isna(atr) or atr <= 0:
            return False
        slope = sma20 - prev
        if abs(slope) < 0.2 * atr:
            return False
        return close > sma20 and slope > 0

    def _indicators(self, df):
        if self._cache_id is id(df) and self._fast is not None:
            return
        prev_close = df["close"].shift(1)
        tr = pd.concat(
            [
                df["high"] - df["low"],
                (df["high"] - prev_close).abs(),
                (df["low"] - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        self._fast = df["close"].ewm(span=self.fast_period, adjust=False).mean()
        self._slow = df["close"].ewm(span=self.slow_period, adjust=False).mean()
        self._atr = tr.rolling(self.atr_period).mean()
        self._cache_id = id(df)

    def check_setup(self, df, current_index):
        """
        Лонг только если:
        1) быстрая средняя выше медленной (локальный up-тренд);
        2) свеча коснулась быстрой средней снизу и закрылась выше неё бычьим телом (откат);
        3) старшие часы (H1) тоже растут;
        4) стоп ниже минимума отката, риск не меньше 0.3 ATR.
        """
        need = max(self.slow_period, self.atr_period) + 1
        if current_index < need:
            return None
        self._indicators(df)

        fast = self._fast.iloc[current_index]
        slow = self._slow.iloc[current_index]
        atr = self._atr.iloc[current_index]
        if pd.isna(fast) or pd.isna(slow) or pd.isna(atr) or atr <= 0:
            return None
        if fast <= slow:
            return None

        candle = df.iloc[current_index]
        touched_fast = candle["low"] <= fast
        closed_above = candle["close"] > fast and candle["close"] > candle["open"]
        if not (touched_fast and closed_above):
            return None

        entry_price = candle["close"]
        sl_price = candle["low"] - self.sl_atr_buffer * atr
        risk_dist = entry_price - sl_price
        if risk_dist < self.min_risk_atr * atr:
            return None

        signal_time = df.index[current_index] + timedelta(minutes=self.bar_minutes)
        if not self._h1_is_bull(signal_time):
            return None

        return {
            "entry_price": entry_price,
            "sl_price": sl_price,
            "direction": "long",
        }
