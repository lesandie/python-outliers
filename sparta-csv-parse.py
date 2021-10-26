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
from datetime import datetime, timedelta

from numpy import False_, log

def check_datetime(date_time):
    """ 
        Input is a string in the %Y-%m-%dT%H:%M:%S format
        Returns False if the input is not in the corret format 
        and the datetime object if the string is well formatted
    """
    try:
        #strptime raise ValueError if not a datetime
        date_time_obj = datetime.strptime(date_time,'%d.%m.%y %H:%M')
    except ValueError:
        logging.error(f'Timestamp error format: {date_time} should be like dd.mm.yy h:m, ignoring row')
        return False
    else:
        #if there isn't any ValueError
        return(date_time_obj)

def check_filepath(filepath):
    """
        Checks if the input path is correct and a file exists
    """
    if os.path.isfile(filepath):
        return True
    else:
        print('File does not exist!: enter the correct path')
        return False                     

async def main():
    # Check if env var TOKEN is set:
    logging.basicConfig(level=logging.DEBUG, filename='csv_parse.log', filemode='w',format='%(asctime)s - %(levelname)s - %(process)d - %(message)s')
    # argument parsing
    parser = argparse.ArgumentParser(description='utility for Sparta csv parsing',
                                     epilog="Example: python sparta_csv_parse.py /path/to/filename")
    # args
    parser.add_argument('filepath', type=str, help='Path to the input file')
    # parse arguments
    args = parser.parse_args()
    # check_input_parameters returns True or False if all the params are correct
    if check_filepath(args.filepath) is not False:
        async with aiofiles.open(args.filepath, mode="r", encoding="utf-8-sig", newline="\n") as afp, \
                    aiofiles.open("new_rbob_data.csv", mode="w", encoding="utf-8-sig", newline="\n") as afp2:
            sep21x = []
            sep21y = []
            index = 0
            window = []
            writer = AsyncDictWriter(afp2)
            async for row in AsyncDictReader(afp, delimiter=","):
                print(row.keys())
                date_item = check_datetime(row['generated_on'])
                value = float(row['dlvd_price'])
                if row['load_month'] == 'Feb.22' and date_item is not False:
                    sep21x.append(date_item)
                    sep21y.append(value)
                    index += 1
                if index > 4:
                    window.pop(0)
                    window.append(value)
                    index = 0
                else:
                    window.append(value)
                avg = sum(window) / len(window)
                std = statistics.stdev(window)
                zscore = (value - avg) / std
                if zscore > 2 or zscore < -2:
                    logging.info(f'outlier detected: {value}')
                else:
                    #await writer.writeheader()
                    await writer.writerow(row)
        
        # Preparing data to plot
        sep21y = sorted(sep21y)
        sep21x = sorted(sep21x)
        print(sep21y)
        plt.style.use('seaborn')
        hfmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.patch.set_facecolor('lightgrey')
        hourlocator = mdates.HourLocator(interval = 12)
        #daylocator = mdates.DayLocator(interval = 1)
        ax.xaxis.set_major_formatter(hfmt)
        #ax.xaxis.set_major_locator(daylocator)
        ax.xaxis.set_major_locator(hourlocator)
        ax.set_title('Sparta Data Test')
        ax.set_xlabel('generated_on')
        ax.set_ylabel('dldv_price')
        #plt.setp(ax.get_xticklabels(), size=8)
        ax.plot(mdates.date2num(sep21x), sep21y, linewidth=2)
        plt.grid()
        plt.show()

if __name__ == '__main__':
    asyncio.run(main())
