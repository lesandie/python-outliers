from csv import DictReader, DictWriter
import argparse
from datetime import datetime
from loadmonth import LoadMonth
from functions import *

def main():
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
        with open(args.filepath, mode="r", encoding="utf-8-sig", newline="\n") as fhandler, \
                    open("new_rbob_data.csv", mode="w", encoding="utf-8-sig", newline="\n") as fhandlew:
            #Init load_month objects
            sep21 = LoadMonth('Sep.21')
            oct21 = LoadMonth('Oct.21')
            nov21 = LoadMonth('Nov.21')
            dec21 = LoadMonth('Dec.21')
            jan22 = LoadMonth('Jan.22')
            feb22 = LoadMonth('Feb.22')
            # init last current date and z_score
            current_date = datetime(1970,1,1,0,0)
            z_score = None
            # if not provided in the constructor, at least one row has to be retrieved before getting the fieldnames.
            areader = DictReader(fhandler, delimiter=",")
            #now we can get the fieldnames
            awriter = DictWriter(fhandlew, areader.fieldnames)
            awriter.writeheader()
            #begin the readline process and calculus
            for row in areader:
                #read line
                date_item = check_datetime(row['generated_on'])
                value = float(row['dlvd_price'])
                if date_item >= current_date:
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
                elif date_item < current_date:
                    # process anomalous order value
                    if row['load_month'] == 'Sep.21' and date_item is not None:
                        z_score = order_insert(date_item, value, sep21)
                    elif row['load_month'] == 'Oct.21' and date_item is not None:
                        z_score = order_insert(date_item, value, oct21)
                    elif row['load_month'] == 'Nov.21' and date_item is not None:
                        z_score = order_insert(date_item, value, nov21)
                    elif row['load_month'] == 'Dec.21' and date_item is not None:
                        z_score = order_insert(date_item, value, dec21)
                    elif row['load_month'] == 'Jan.22' and date_item is not None:
                        z_score = order_insert(date_item, value, jan22)
                    elif row['load_month'] == 'Feb.22' and date_item is not None:
                        z_score = order_insert(date_item, value, feb22)
                    else:
                        raise ValueError('Load Month is not in the expected list')
                else:
                    logging.error(f"Current date is None ---> {current_date}")
                
                #Now checking for outliers if not write to file. If z_score is None the date is wrong
                if z_score is not None:
                    if z_score > 40 or z_score < -40:
                        logging.info('------------------------------------------------------------------------------------------------------------')
                        logging.info(f'''Outlier detected in {row['load_month']} for date {date_item.strftime('%Y-%m-%d %H:%M:%S')}: value {value} and zscore {z_score}''')
                    else:
                        #Change the string format to another
                        row['generated_on'] = date_item.strftime('%Y-%m-%d %H:%M:%S')
                        awriter.writerow(row)
                else:
                    logging.error(f"Error updating the timeseries for {date_item} and {value} with zscore: {z_score}") 
        #plot graph
        plot_graph(sep21, oct21, nov21, dec21, jan22, feb22)
        
if __name__ == '__main__':
    main()
