from datetime import datetime
from nptyping import NDArray
from typing import Any, List
import numpy as np

class LoadMonth():
    def __init__(
        self,
        name
    ):
        self.name = name
        self.__timeseries = {}
        self.__current_window = np.empty(0, dtype=np.float16)
    
    def load_data(self, key: datetime, value: float, window: NDArray[Any]):
        # The value is in the index 0 of the array 
        self.__timeseries[key] = np.insert(window, 0, value)
    
    def get_value(self, key: datetime) -> NDArray[Any]:
        return self.__timeseries[key]
    
    def get_keys(self) -> List:
        return list(self.__timeseries.keys())

    def get_xaxis(self):
        d_ordered = dict(sorted(self.__timeseries.items()))
        return np.array(list(d_ordered.keys()), dtype='datetime64')

    def get_yaxis(self):
        d_ordered = dict(sorted(self.__timeseries.items()))
        return np.array(
                    [i[0] for i in list(d_ordered.values())], 
                    dtype=np.float16
                    )
    
    def window_append(self, win: float):
        self.__current_window = np.append(self.__current_window, win)

    def window_pop(self):
        self.__current_window = np.delete(self.__current_window, 0)
    
    def window_get(self) -> NDArray[Any]:
        return self.__current_window