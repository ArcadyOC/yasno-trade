import pandas as pd
from base_strategy import BaseStrategy


class VolumeImpulseStrategy(BaseStrategy):
    """Ловит начало резкого хода: диапазон свечи и объём заметно выше обычного, не шум."""

    def __init__(self):
        self.name = "Volume Impulse"
        self.atr_period = 14
        self.vol_period = 20
        self.range_atr_mult = 1.4
        self.vol_mult = 1.5
        self.sl_atr_buffer = 0.3
        self.min_risk_atr = 0.4
        self._cache_id = None
        self._atr = None
        self._vol_avg = None

    def _indicators(self, df):
        if self._cache_id is id(df) and self._atr is not None:
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
        self._atr = tr.rolling(self.atr_period).mean()
        if "tick_volume" in df.columns:
            self._vol_avg = df["tick_volume"].rolling(self.vol_period).mean()
        else:
            self._vol_avg = None
        self._cache_id = id(df)

    def check_setup(self, df, current_index):
        """
        Лонг только если:
        1) диапазон свечи заметно больше обычного ATR (импульс, а не шум);
        2) объём тиков выше среднего за 20 баров минимум в 1.5 раза;
        3) свеча бычья, закрытие в верхней половине диапазона.
        """
        need = max(self.atr_period, self.vol_period) + 1
        if current_index < need:
            return None
        self._indicators(df)
        if self._vol_avg is None:
            return None

        candle = df.iloc[current_index]
        atr = self._atr.iloc[current_index]
        vol_avg = self._vol_avg.iloc[current_index]
        if pd.isna(atr) or atr <= 0 or pd.isna(vol_avg) or vol_avg <= 0:
            return None

        candle_range = candle["high"] - candle["low"]
        if candle_range < self.range_atr_mult * atr:
            return None

        volume = candle.get("tick_volume")
        if volume is None or pd.isna(volume) or volume < self.vol_mult * vol_avg:
            return None

        if candle["close"] <= candle["open"]:
            return None
        if candle["close"] < candle["low"] + candle_range * 0.5:
            return None

        entry_price = candle["close"]
        sl_price = candle["low"] - self.sl_atr_buffer * atr
        risk_dist = entry_price - sl_price
        if risk_dist < self.min_risk_atr * atr:
            return None

        return {
            "entry_price": entry_price,
            "sl_price": sl_price,
            "direction": "long",
        }
