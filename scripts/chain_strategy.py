import pandas as pd
from base_strategy import BaseStrategy


class ElasticReclaimStrategy(BaseStrategy):
    """Резинка: цена растянута от средней вниз, потом ложный пробой лоя и возврат внутрь."""

    def __init__(self):
        self.name = "Elastic Reclaim (chain)"
        self.sma_period = 20
        self.atr_period = 14
        self.stretch_atr = 1.5
        self.lookback = 8
        self.sl_atr_buffer = 0.2
        self.min_risk_atr = 0.3
        self._cache_id = None
        self._sma = None
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
        self._sma = df["close"].rolling(self.sma_period).mean()
        self._atr = tr.rolling(self.atr_period).mean()
        self._cache_id = id(df)

    def check_setup(self, df, current_index):
        """
        Лонг только если:
        1) 2-4 бара назад цена была растянута вниз от SMA20 (не меньше 1.5 ATR) — «резинка»;
        2) прошлый бар пробил минимум последних lookback баров — ложный выход за край;
        3) текущий бар закрылся обратно выше этого минимума бычьим телом — возврат.
        """
        need = max(self.sma_period, self.atr_period, self.lookback) + 4
        if current_index < need:
            return None
        self._indicators(df)

        atr = self._atr.iloc[current_index]
        if pd.isna(atr) or atr <= 0:
            return None

        stretch_close = df["close"].iloc[current_index - 4 : current_index - 1]
        stretch_sma = self._sma.iloc[current_index - 4 : current_index - 1]
        stretched = ((stretch_sma - stretch_close) >= self.stretch_atr * atr).any()
        if not stretched:
            return None

        prior = df.iloc[current_index - 1]
        prior_low = df["low"].iloc[current_index - 1 - self.lookback : current_index - 1].min()
        if pd.isna(prior_low) or prior["low"] >= prior_low:
            return None

        candle = df.iloc[current_index]
        if not (candle["close"] > prior_low and candle["close"] > candle["open"]):
            return None

        entry_price = candle["close"]
        sl_price = min(prior["low"], candle["low"]) - self.sl_atr_buffer * atr
        risk_dist = entry_price - sl_price
        if risk_dist < self.min_risk_atr * atr:
            return None

        return {
            "entry_price": entry_price,
            "sl_price": sl_price,
            "direction": "long",
        }
