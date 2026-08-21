import pandas as pd
from data_engine import MT5DataFetcher
import MetaTrader5 as mt5
from pinbar_strategy import PinbarSweepStrategy


class EventLoopSimulator:
    def __init__(self, df: pd.DataFrame, strategy):
        self.data = df
        self.strategy = strategy
        self.setups_realized = []
        self.entry_weekdays = []

    def run_simulation(self, target_r=2.5):
        in_setup_progress = False
        sl_price = 0.0
        tp_price = 0.0
        pending_weekday = None

        print(f"Запуск аудита для стратегии: {self.strategy.name}")

        def close_trade(result):
            self.setups_realized.append(result)
            self.entry_weekdays.append(pending_weekday)

        for i in range(1, len(self.data)):
            current_candle = self.data.iloc[i]

            if in_setup_progress:
                if current_candle["low"] <= sl_price:
                    close_trade(-1.0)
                    in_setup_progress = False
                elif current_candle["high"] >= tp_price:
                    close_trade(target_r)
                    in_setup_progress = False
                continue

            setup = self.strategy.check_setup(self.data, i)
            if setup and setup["direction"] == "long":
                entry_price = setup["entry_price"]
                sl_price = setup["sl_price"]
                risk_dist = entry_price - sl_price
                if risk_dist > 0:
                    tp_price = entry_price + (risk_dist * target_r)
                    in_setup_progress = True
                    pending_weekday = self.data.index[i].day_name()

        return self.setups_realized


if __name__ == "__main__":
    fetcher = MT5DataFetcher()
    df_gold = fetcher.fetch_clean_data("XAUUSD", mt5.TIMEFRAME_M15, 3000)
    df_h1 = fetcher.fetch_clean_data("XAUUSD", mt5.TIMEFRAME_H1, 2000)
    fetcher.disconnect()

    if not df_gold.empty:
        my_strategy = PinbarSweepStrategy()
        my_strategy.set_hourly_context(df_h1)

        simulator = EventLoopSimulator(df_gold, my_strategy)
        results = simulator.run_simulation(target_r=2.5)

        total_setups = len(results)
        win_count = sum(1 for r in results if r > 0)
        loss_count = sum(1 for r in results if r < 0)
        total_r = sum(results)

        print("\n=== ПАСПОРТ ГИПОТЕЗЫ ===")
        print(f"Проверено свечей: {len(df_gold)}")
        print(f"Найдено сетапов: {total_setups}")
        print(f"Пропущено из-за бычьего H1: {my_strategy.skipped_h1_bull}")
        if total_setups > 0:
            print(f"Плюсы / минусы: {win_count} / {loss_count}")
            print(f"Точность (Win Rate): {(win_count / total_setups) * 100:.1f}%")
            print(f"Итоговый баланс (R): {total_r:.2f} R")
            print(f"Мат. ожидание (EV): {total_r / total_setups:.2f} R на каждый сетап")
            print("По дням недели:")
            for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
                day_rs = [r for r, d in zip(results, simulator.entry_weekdays) if d == day]
                if not day_rs:
                    continue
                d_win = sum(1 for r in day_rs if r > 0)
                print(
                    f"  {day}: n={len(day_rs)}  WR={(d_win / len(day_rs)) * 100:.0f}%  "
                    f"R={sum(day_rs):.1f}"
                )
