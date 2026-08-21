class BaseStrategy:
    def __init__(self):
        self.name = "Abstract Strategy"
        
    def check_setup(self, df_slice, current_index):
        """
        Эта функция анализирует кусок графика до текущей свечи.
        Должна вернуть словарь с координатами сетапа, если он есть, 
        или None, если рынок не дает четкого сигнала.
        """
        return None