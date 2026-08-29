import pandas as pd
from base_strategy import BaseStrategy


class SqueezeBreakoutStrategy(BaseStrategy):
    """Сжатие полос Боллинджера, потом сильный выход за верхний край — но не в перегретый рынок."""

    def __init__(self):
        self.name = "Squeeze Breakout (observe)"
        self.bb_period = 20
        self.bb_mult = 2.0
        self.atr_period = 14
        self.squeeze_pct = 0.25
        self.squeeze_lookback = 100
        self.breakout_atr_mult = 1.0
        self.overheat_atr_mult = 3.5
        self.sl_atr_buffer = 0.2
        self.min_risk_atr = 0.3
        self._cache_id = None
        self._sma = None
        self._upper = None
        self._width = None
        self._atr = None

    def _indicators(self, df):
        if self._cache_id is id(df) and self._sma is not None:
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
        sma = df["close"].rolling(self.bb_period).mean()
        std = df["close"].rolling(self.bb_period).std()
        self._sma = sma
        self._upper = sma + self.bb_mult * std
        self._width = (2 * self.bb_mult * std) / sma.abs().replace(0, pd.NA)
        self._atr = tr.rolling(self.atr_period).mean()
        self._cache_id = id(df)

    def check_setup(self, df, current_index):
        """
        Лонг только если:
        1) прошлый бар был в сжатии (ширина полос в нижних 25% за последние 100 баров);
        2) текущий бар закрылся выше верхней полосы сильным ходом (диапазон больше ATR);
        3) рынок ещё не перегрет (цена не дальше 3.5 ATR от SMA20).
        """
        need = max(self.bb_period, self.atr_period, self.squeeze_lookback) + 2
        if current_index < need:
            return None
        self._indicators(df)

        atr = self._atr.iloc[current_index]
        if pd.isna(atr) or atr <= 0:
            return None

        width_hist = self._width.iloc[current_index - self.squeeze_lookback : current_index - 1].dropna()
        prev_width = self._width.iloc[current_index - 1]
        if width_hist.empty or pd.isna(prev_width):
            return None
        threshold = width_hist.quantile(self.squeeze_pct)
        if prev_width > threshold:
            return None

        candle = df.iloc[current_index]
        upper = self._upper.iloc[current_index]
        sma = self._sma.iloc[current_index]
        if pd.isna(upper) or pd.isna(sma):
            return None
        if candle["close"] <= upper:
            return None

        candle_range = candle["high"] - candle["low"]
        if candle_range < self.breakout_atr_mult * atr:
            return None

        if (candle["close"] - sma) > self.overheat_atr_mult * atr:
            return None

        entry_price = candle["close"]
        sl_price = sma
        risk_dist = entry_price - sl_price
        if risk_dist < self.min_risk_atr * atr:
            sl_price = candle["low"] - self.sl_atr_buffer * atr
            risk_dist = entry_price - sl_price
            if risk_dist < self.min_risk_atr * atr:
                return None

        return {
            "entry_price": entry_price,
            "sl_price": sl_price,
            "direction": "long",
        }
