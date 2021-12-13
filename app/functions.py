# MAIN FUNCTIONS
#from __futures__ import annotations
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime
from app.loadmonth import LoadMonth
from typing import Union, Any
from nptyping import NDArray
from scipy import stats
import numpy as np


def check_datetime(date_time) -> datetime:
    """ 
    Input is a string in the %Y-%m-%dT%H:%M:%S format
    Returns False if the input is not in the corret format 
    and the datetime object if the string is well formatted
    """
    POSSIBLE_DATE_FORMATS = ['%d.%m.%y %H:%M', '%Y-%m-%d %H:%M:%S.%f'] # all the formats the date might be in
    for date_format in POSSIBLE_DATE_FORMATS:
        try:
            date_time_obj = datetime.strptime(date_time, date_format) # try to get the date
            #logging.warning(f'Timestamp {date_time} has format {date_format}')
            return(date_time_obj)# if correct format, don't test any other formats
        except ValueError:
            #logging.error(f'Timestamp {date_time} is not formatted like {date_format} ... testing more formats')
            pass # if incorrect format, keep trying other formats    
    raise ValueError(f'Timestamp {date_time} format not detected, consider adding the new format to POSSIBLE_DATE_FORMATS')
   
def check_filepath(filepath) -> bool:
    """
    Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        print('File does not exist!: enter the correct path')
        return False

def get_zscore(value, window: NDArray[Any]) -> float:
    """
    Calculates the zscore
    """
    # Insert value in the index0
    value = round(value,2)
    # If there are 3 or more values of difference
    if len(window) > 0:
        if abs(value - np.average(window)) < 3:
            return 0.00     
        else:
            zscore = stats.zscore(np.insert(window, 0, value))[0]
            return round(zscore,2)
    else:
        return 0.00

def plot_graph(*args: LoadMonth):
    """
    Plotter
    """
    # Preparing to plot
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=12))
    ax.tick_params(which='major', labelsize=8, labelbottom=True)
    ax.tick_params(which='minor', labelsize=6, color='r', labeltop=True)
    ax.grid()
    #plot graphs
    for arg in args:
        ax.plot(arg.get_xaxis(), arg.get_yaxis(), label=arg.name)
    plt.figure(fig)
    plt.title("Sparta Data Test",fontsize=13)
    plt.xlabel("Timeline",fontsize=8)
    plt.ylabel("Price",fontsize=8)
    plt.legend()
    plt.show()                     

def process_csv_row(date_item, value, month: LoadMonth) -> float:
    """
    Process each row and modifies the time window to adapt it to the last value
    """
    zscore = get_zscore(value, month.window_get())
    #update window for zscore using the last 4 timestamps = last hour
    if len(month.window_get()) > 3:
        month.window_pop()
    month.window_append(value)
    month.load_data(date_item, value, month.window_get())
    return zscore
 
def order_insert(date_item, value, month: LoadMonth) -> Union[float, None]:
    """
    Inserts the date into the structure
    """
    dates = month.get_keys()
    if date_item not in dates:
        prev = [i for i in dates if i < date_item]
        next = [i for i in dates if i >= date_item]
        # Extracts the followind date and the prior date to date_item
        prev_elem = prev[-1]
        next_elem = next[0]
        if prev_elem != next_elem:
            # get_value returns the value at position 0 and the window of that time.
            # Simply select the last two window items from the prev_elem and the two first elements of the next_elem
            # and concatenate to a new window
            calc_win = np.concatenate((month.get_value(prev_elem)[3:5], month.get_value(next_elem)[1:3]))
            month.load_data(date_item, value, calc_win)
            zscore = get_zscore(value, calc_win)
            logging.info(f"Not ordered sequence of {date_item} with value: {value} with window: {calc_win} and zscore: {zscore}")
            return zscore
        else:
            logging.error(f"timeseries malformed please check the log")
            return None
    else:
        raise KeyError(f"Key {date_item} already exists!")