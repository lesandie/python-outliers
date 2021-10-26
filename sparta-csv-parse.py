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
            logging.error(f'Timestamp {date_time} is not formatted like {date_format} ... testing more formats')
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

def plot_graph(axis_x_list, axis_y_list):
    # Preparing data to plot
        axis_y_list = sorted(axis_y_list)
        axis_x_list = sorted(axis_x_list)
        hfmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        fig = plt.figure()
        ax = fig.add_subplot()
        #ax.patch.set_facecolor('lightgrey')
        hourlocator = mdates.HourLocator(interval = 12)
        #daylocator = mdates.DayLocator(interval = 1)
        ax.xaxis.set_major_formatter(hfmt)
        #ax.xaxis.set_major_locator(daylocator)
        ax.xaxis.set_major_locator(hourlocator)
        ax.set_title('Sparta Data Test')
        ax.set_xlabel('generated_on')
        ax.set_ylabel('dldv_price')
        #plt.setp(ax.get_xticklabels(), size=8)
        ax.plot(mdates.date2num(axis_x_list), axis_y_list, linewidth=2)
        plt.grid()
        plt.show()                     

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
            sep21x = []
            sep21y = []
            index = 0
            window = []
            # Unlike csv.DictReader
            # if not provided in the constructor, at least one row has to be retrieved before getting the fieldnames.
            areader = AsyncDictReader(fhandler, delimiter=",")
            await areader.__anext__()
            #now we can get the fieldnames
            awriter = AsyncDictWriter(fhandlew, areader.fieldnames)
            await awriter.writeheader()
            #begin the readline process and calculus
            async for row in areader:
                #reset the time window for localities
                if index > 4:
                    window.pop(0)
                    window.append(value)
                    index = 0
                # read line
                date_item = check_datetime(row['generated_on'])
                value = float(row['dlvd_price'])
                # append to lists
                if row['load_month'] == 'Feb.22' and date_item is not None:
                    sep21x.append(date_item)
                    sep21y.append(value)
                    # append to window
                    window.append(value)
                    index += 1
                    avg = sum(window) / len(window)
                    #std function needs at least two values to compute
                    if index > 2:
                        std = statistics.stdev(window)
                    else:
                        std = 1
                    zscore = (value - avg) / std
                    if zscore > 2 or zscore < -2:
                        logging.info(f'outlier detected: {value}')
                    else:
                        await awriter.writerow(row)
        #plot graph
        plot_graph(sep21x,sep21y)

if __name__ == '__main__':
    asyncio.run(main())
