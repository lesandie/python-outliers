import numpy as np
from numpy import ndarray
from datetime import datetime
from typing import Any, List, TypeVar

# 3.11 feature type hint for Array of np.floats16
NPArray = TypeVar("NPArray", bound=np.float16)
NDArray = TypeVar("NDArray", bound=np.datetime64)


class LoadMonth:
    def __init__(
        self,
        name
    ):
        self.name = name
        self.__timeseries = {}
        self.__current_window = np.empty(0, dtype=np.float16)
    
    def load_data(self, key: datetime, value: float, window: ndarray) -> None:
        # The value is in the index 0 of the array 
        self.__timeseries[key] = np.insert(window, 0, value)
    
    def get_value(self, key: datetime) -> ndarray:
        return self.__timeseries[key]
    
    def get_keys(self) -> List:
        return list(self.__timeseries.keys())

    def get_xaxis(self) -> ndarray:
        d_ordered = dict(sorted(self.__timeseries.items()))
        return np.array(list(d_ordered.keys()), dtype=np.datetime64)

    def get_yaxis(self) -> ndarray:
        d_ordered = dict(sorted(self.__timeseries.items()))
        return np.array(
                    [i[0] for i in list(d_ordered.values())], 
                    dtype=np.float16
                    )
    
    def window_append(self, win: float):
        self.__current_window = np.append(self.__current_window, win)

    def window_pop(self):
        self.__current_window = np.delete(self.__current_window, 0)
    
    def window_get(self) -> ndarray:
        return self.__current_window
