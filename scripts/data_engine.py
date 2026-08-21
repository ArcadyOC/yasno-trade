import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import pytz

class MT5DataFetcher:
    def __init__(self):
        # Инициализация подключения к открытому терминалу MT5
        if not mt5.initialize():
            print(f"Ошибка инициализации MT5: {mt5.last_error()}")
            quit()
        print("Связь с MT5 установлена. Ясность потока данных обеспечена.")

    def fetch_clean_data(self, symbol: str, timeframe, num_candles: int) -> pd.DataFrame:
        """
        Запрашивает свечи и проводит санитарную очистку: 
        только закрытые свечи, конвертация времени в UTC.
        """
        # Запрашиваем на 1 свечу больше, чтобы откинуть текущую (незакрытую) свечу
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles + 1)
        
        if rates is None:
            print(f"Ошибка получения данных для {symbol}: {mt5.last_error()}")
            return pd.DataFrame()

        df = pd.DataFrame(rates)
        
        # Конвертация времени из формата UNIX (EET брокера) в читабельный UTC
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Откидываем последнюю строку (текущую живую свечу), 
        # чтобы алгоритм не заглядывал в будущее
        df = df.iloc[:-1].copy()
        
        # Оставляем только нужный для чистой математики фундамент
        df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        df.set_index('time', inplace=True)
        
        return df

    def disconnect(self):
        mt5.shutdown()

if __name__ == "__main__":
    # Настраиваем инструмент и таймфрейм (M15)
    SYMBOL = "XAUUSD"
    TIMEFRAME = mt5.TIMEFRAME_M15
    CANDLES_TO_FETCH = 1000  # Примерно 10-12 дней интрадей данных

    fetcher = MT5DataFetcher()

    print(f"Запрашиваем исторические данные: {SYMBOL}...")
    df_gold = fetcher.fetch_clean_data(SYMBOL, TIMEFRAME, CANDLES_TO_FETCH)

    if not df_gold.empty:
        print("\nСанитарный контроль пройден. Фрагмент очищенного датасета:")
        print(df_gold.tail())  # Показываем последние 5 закрытых свечей
        print(f"\nВсего загружено: {len(df_gold)} рабочих интервалов.")

    fetcher.disconnect()