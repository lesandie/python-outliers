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
        self.__dlvd_val = []
        self.__timestamps = []
        self.__window = []
    
    def load_data(self, timestamps, dlvd_val):
        self.__timestamps.append(timestamps)
        self.__dlvd_val.append(dlvd_val)
    
    def get_xaxis(self):
        return self.__timestamps

    def get_yaxis(self):
        return self.__dlvd_val

    def window_append(self, win):
        self.__window.append(win)

    def window_pop(self):
        self.__window.pop(0)
    
    def window_get(self):
        return self.__window

def check_datetime(date_time):
    """ 
        Input is a string in the %Y-%m-%dT%H:%M:%S format
        Returns False if the input is not in the corret format 
        and the datetime object if the string is well formatted
    """
    POSSIBLE_DATE_FORMATS = ["%d.%m.%y %H:%M", "%Y-%m-%d %H:%M:%S.%f"] # all the formats the date might be in
    for date_format in POSSIBLE_DATE_FORMATS:
        try:
            date_time_obj = datetime.strptime(date_time, date_format) # try to get the date
            logging.info(f'Timestamp {date_time} has format {date_format}')
            return(date_time_obj)# if correct format, don't test any other formats
        except ValueError:
            #logging.error(f'Timestamp {date_time} is not formatted like {date_format} ... testing more formats')
            pass # if incorrect format, keep trying other formats    
    raise ValueError('no valid date format found')
   
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
    avg = sum(window) / len(window)
    #std function needs at least two values to compute
    if len(window) > 2:
        std = statistics.stdev(window)
    else:
        std = 1
    #std of the same values is 0. Avoid the ZeroDivision exception
    if std == 0 or std ==1:
        return (value - avg)
    else:
        return (value - avg) / std


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
        process each row and modifies the time window to dapt it to the last value
    """
    #update window for zscore i use the last 3 timestamps = last 45 mins
    if len(month.window_get()) > 2:
        month.window_pop()
    #load data into the object
    month.load_data(date_item, value)
    month.window_append(value)
    # count up for the window
    return get_zscore(value, month.window_get())

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
                # process rows
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
                #Now checking for outliers if not write to file
                if z_score > 2 or z_score < -2:
                    logging.info('-----------------------------------------------------')
                    logging.info(f'''Outlier detected in {row['load_month']}: {value}''')
                    logging.info('-----------------------------------------------------')
                else:
                    await awriter.writerow(row)      
        #plot graph
        plot_graph(sep21, oct21, nov21, dec21, jan22, feb22)

if __name__ == '__main__':
    asyncio.run(main())
