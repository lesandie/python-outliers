import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics
import sys
import asyncio
import os
import csv
import aiofiles
from aiocsv import AsyncDictReader, AsyncDictWriter
import time
import argparse
from datetime import datetime

class LoadMonth():
    def __init__(
        self,
        name
    ):
        self.name = name
        self.timeseries = {}
        self.__window = []
    
    def load_data(self, key, value, window):
        self.timeseries[key] = list(value, window)
    
    def get_value(self, key):
        return self.timeseries[key]

    def get_xaxis(self):
        d_ordered = dict(sorted(self.timeseries.items()))
        return list(d_ordered.keys())

    def get_yaxis(self):
        d_ordered = dict(sorted(self.timeseries.items()))
        return list(d_ordered.values())

    def window_append(self, win):
        self.__window.append(win)

    def window_pop(self):
        self.__window.pop(0)
    
    def window_get(self):
        return self.__window

# MAIN FUNCTIONS

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
    #update window for zscore i use the last 4 timestamps = last 45 mins
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

async def main():
    # Set logging level
    logging.basicConfig(level=logging.INFO, filename='csv_parse.log', filemode='w',format='%(asctime)s - %(levelname)s - %(process)d - %(message)s')
    # argument parsing
    parser = argparse.ArgumentParser(description='utility for Sparta csv parsing',
                                     epilog="Example: python sparta_csv_parse.py /path/to/filename")
    # args
    parser.add_argument('filepath', type=str, help='Path to the input file')
    # parse arguments
    args = parser.parse_args()
    # check_input_parameters returns True or False if all the params are correct
    if check_filepath(args.filepath) is not False:
        async with aiofiles.open(args.filepath, mode="r", encoding="utf-8-sig", newline="\n") as fhandler, \
                    aiofiles.open("new_rbob_data.csv", mode="w", encoding="utf-8-sig", newline="\n") as fhandlew:
            #Init load_month objects
            sep21 = LoadMonth('Sep.21')
            oct21 = LoadMonth('Oct.21')
            nov21 = LoadMonth('Nov.21')
            dec21 = LoadMonth('Dec.21')
            jan22 = LoadMonth('Jan.22')
            feb22 = LoadMonth('Feb.22')
            # init last current date
            current_date: datetime = None
            # Unlike csv.DictReader
            # if not provided in the constructor, at least one row has to be retrieved before getting the fieldnames.
            areader = AsyncDictReader(fhandler, delimiter=",")
            await areader.__anext__()
            #now we can get the fieldnames
            awriter = AsyncDictWriter(fhandlew, areader.fieldnames)
            await awriter.writeheader()
            #begin the readline process and calculus
            async for row in areader:
                #read line
                date_item = check_datetime(row['generated_on'])
                value = float(row['dlvd_price'])
                if current_date is not None and date_item > current_date:
                    current_date = date_item
                    # process rows normally
                    if row['load_month'] == 'Sep.21' and date_item is not None:
                        z_score = process_csv_row(date_item, value, sep21)
                    elif row['load_month'] == 'Oct.21' and date_item is not None:
                        z_score = process_csv_row(date_item, value, oct21)
                    elif row['load_month'] == 'Nov.21' and date_item is not None:
                        z_score = process_csv_row(date_item, value, nov21)
                    elif row['load_month'] == 'Dec.21' and date_item is not None:
                        z_score = process_csv_row(date_item, value, dec21)
                    elif row['load_month'] == 'Jan.22' and date_item is not None:
                        z_score = process_csv_row(date_item, value, jan22)
                    elif row['load_month'] == 'Feb.22' and date_item is not None:
                        z_score = process_csv_row(date_item, value, feb22)
                    else:
                        raise ValueError('Load Month is not in the expected list')
                else:
                    # insert the date into the structure
                    if date_item not in dec21.timeseries:
                        prev_elem = next(i for i in dec21.timeseries.keys() if i < date_item)
                        next_elem = next(i for i in dec21.timeseries.keys() if i >= date_item)
                        if prev_elem != next_elem:
                            calc_win = dec21.get_value(prev_elem)[0][0:2] + dec21.get_value(next_elem)[0][0:2]
                            sep21.load_data(date_item, value, calc_win)
                            z_score = get_zscore(value, calc_win)
                    else:
                        raise KeyError

                #Now checking for outliers if not write to file. If z_score is None the date is wrong
                if z_score > 50 or z_score < -50:
                    logging.info('------------------------------------------------------------------------------------------------------------')
                    logging.info(f'''Outlier detected in {row['load_month']} for date {date_item.strftime('%Y-%m-%d %H:%M:%S')}: value {value} and zscore {z_score}''')
                else:
                    #Change the string format to another
                    row['generated_on'] = date_item.strftime('%Y-%m-%d %H:%M:%S')
                    await awriter.writerow(row)
                    #csv_out = csv_out | row      
            #Write file        
        #plot graph
        #plot_graph(sep21, oct21, nov21, dec21, jan22, feb22)
        d_ordered = dict(sorted(dec21.timeseries.items()))
        print(f'{dec21.timeseries.values()}')
        plot_graph(dec21)
if __name__ == '__main__':
    asyncio.run(main())
