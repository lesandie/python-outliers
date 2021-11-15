# MAIN FUNCTIONS
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics
import os
from datetime import datetime
from loadmonth import LoadMonth

def check_datetime(date_time):
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
   
def check_filepath(filepath):
    """
        Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        print('File does not exist!: enter the correct path')
        return False

def get_zscore(value, window):
    """
        Calculates the zscore
    """
    #std function needs at least two values to compute
    if len(window) < 3:
       return 0
    else:
        value = round(value,2)
        avg = sum(window) / len(window)
        avg = round(avg,2)
        std = statistics.stdev(window)
        std = round(std,1)
        #std of the same values is 0. Avoid the ZeroDivision exception
        if std == 0.0:
            print(f'value = {value}')
            print(f'window = {window}')
            print(f'avg = {avg}')
            print(f'stdev = {std}')
            # std is zero but current value is away from the median
            if abs(value - avg) > 3:
                print(f'zscore = 100')
                print('-------------------')
                return 100
            else:
                print(f'zscore = 0.00')
                print('-------------------')
                return 0.00
        else:
            zscore = (value - avg) / std
            print(f'value = {value}')
            print(f'window = {window}')
            print(f'avg = {avg}')
            print(f'stdev = {std}')
            print(f'zscore = {zscore}')
            print('-------------------')
            return round(zscore,2)

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
        ax.plot(mdates.date2num(arg.get_xaxis()), arg.get_yaxis(), label=arg.name)
    #config the figure
    plt.figure(fig)
    plt.title("Sparta Data Test",fontsize=13)
    plt.xlabel("Timeline",fontsize=8)
    plt.ylabel("Price",fontsize=8)
    plt.legend()
    plt.show()                     

def process_csv_row(date_item, value, month: LoadMonth):
    """
        process each row and modifies the time window to adapt it to the last value
    """
    zscore = get_zscore(value, month.window_get())
    #update window for zscore i use the last 4 timestamps = last hour
    if len(month.window_get()) > 3:
        month.window_pop()
    # count up for the window
    month.window_append(value)
    # load the data into the object
    month.load_data(date_item, value, month.window_get())
    #if date_item.strftime('%Y-%m-%d') == '2021-09-23' and month.name == 'Dec.21' and value == -7.15:
    #    print(f'{date_item} and {value}')
    #    print('-------------------')
    return zscore

def order_insert(date_item, value, month: LoadMonth):
    # insert the date into the structure
    dates = month.get_keys()
    if date_item not in dates:
        prev = [i for i in dates if i < date_item]
        next = [i for i in dates if i >= date_item]
        prev_elem = prev.pop(-1)
        next_elem = next.pop(0)
        if prev_elem != next_elem:
            #get_value returns the value and the window of that time
            calc_win = month.get_value(prev_elem)[1][2:] + month.get_value(next_elem)[1][0:2]
            month.load_data(date_item, value, calc_win)
            zscore = get_zscore(value, calc_win)
            return zscore
        else:
            logging.error(f"timeseries malformed please check the log")
            return None
    else:
        raise KeyError(f"Key {date_item} already exists!")