class LoadMonth():
    def __init__(
        self,
        name
    ):
        self.name = name
        self.__timeseries = {}
        self.__current_window = []
    
    def load_data(self, key, value, window):
        self.__timeseries[key] = [value, window]
    
    def get_value(self, key):
        return self.__timeseries[key]
    
    def get_keys(self):
        return self.__timeseries.keys()

    def get_xaxis(self):
        d_ordered = dict(sorted(self.__timeseries.items()))
        return list(d_ordered.keys())

    def get_yaxis(self):
        d_ordered = dict(sorted(self.__timeseries.items()))
        return [i[0] for i in list(d_ordered.values())]
    
    def window_append(self, win):
        self.__current_window.append(win)

    def window_pop(self):
        self.__current_window.pop(0)
    
    def window_get(self):
        return self.__current_window